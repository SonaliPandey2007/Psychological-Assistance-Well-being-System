from flask import Blueprint, jsonify, request

from database.db import get_db_connection
from database.audit import ensure_audit_logs_table, insert_audit_log
from routes.auth import token_required, role_required


officer_bp = Blueprint(
    "officer",
    __name__,
    url_prefix="/api/officer"
)

# Navigation events are intentionally excluded from the audit history view.
# They create noise without adding accountability value.
HIDDEN_AUDIT_ACTIONS = {"VIEW_DASHBOARD", "VIEW_AUDIT_LOG", "VIEW_AUTOLOG", "REFRESH_AUTOLOG"}


# =========================================================
# OFFICER DASHBOARD SUMMARY
# =========================================================

@officer_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("OFFICER")
def dashboard():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Total victims
        cursor.execute("""
            SELECT COUNT(*) AS total_victims
            FROM victims
        """)
        total_victims = cursor.fetchone()["total_victims"]

        # Total cases
        cursor.execute("""
            SELECT COUNT(*) AS total_cases
            FROM cases
        """)
        total_cases = cursor.fetchone()["total_cases"]

        # Active cases
        cursor.execute("""
            SELECT COUNT(*) AS active_cases
            FROM cases
            WHERE case_status = 'ACTIVE'
        """)
        active_cases = cursor.fetchone()["active_cases"]

        # High-risk victims
        cursor.execute("""
            SELECT COUNT(DISTINCT victim_id) AS high_risk_victims
            FROM distress_scores
            WHERE risk_level = 'HIGH'
        """)
        high_risk_victims = cursor.fetchone()["high_risk_victims"]

        # Recent alerts
        cursor.execute("""
            SELECT
                a.alert_id,
                a.victim_id,
                v.victim_code,
                a.severity,
                a.alert_type,
                a.message,
                a.is_reviewed,
                a.created_at
            FROM alerts a
            JOIN victims v
                ON a.victim_id = v.victim_id
            ORDER BY a.created_at DESC
            LIMIT 10
        """)

        recent_alerts = cursor.fetchall()

        # Latest distress score for each victim
        cursor.execute("""
            SELECT
                d.victim_id,
                v.victim_code,
                d.distress_index,
                d.risk_level,
                d.explanation,
                d.created_at
            FROM distress_scores d
            JOIN victims v
                ON d.victim_id = v.victim_id
            INNER JOIN (
                SELECT
                    victim_id,
                    MAX(score_id) AS latest_score_id
                FROM distress_scores
                GROUP BY victim_id
            ) latest
                ON d.score_id = latest.latest_score_id
            ORDER BY d.distress_index DESC
        """)

        victim_risk = cursor.fetchall()

        return jsonify({
            "dashboard": "OFFICER",
            "summary": {
                "total_victims": total_victims,
                "total_cases": total_cases,
                "active_cases": active_cases,
                "high_risk_victims": high_risk_victims
            },
            "recent_alerts": recent_alerts,
            "victim_risk": victim_risk
        }), 200

    except Exception as error:

        print("OFFICER DASHBOARD ERROR:", error)

        return jsonify({
            "error": "Could not load officer dashboard"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# AUDIT LOGS
# =========================================================

@officer_bp.route("/audit-logs", methods=["GET"])
@token_required
def get_audit_logs():
    """Return audit activity using the live audit_logs table schema.

    The existing PAWS database has evolved, so this endpoint deliberately
    reads the table with SELECT * and normalises the available columns in
    Python. That keeps the Officer dashboard working even when optional
    audit columns differ between local database versions.
    """
    connection = None
    cursor = None

    try:
        # Audit Log is for officers only, but keep this check compatible with
        # the existing token payload structure used by the rest of the app.
        role = str(request.user.get("role", "")).upper()
        if role and role != "OFFICER":
            return jsonify({"error": "Officer access required"}), 403

        connection = get_db_connection()
        ensure_audit_logs_table(connection)
        cursor = connection.cursor(dictionary=True)

        try:
            limit = int(request.args.get("limit", 250))
        except (TypeError, ValueError):
            limit = 250
        limit = min(max(limit, 1), 500)

        # Read the live schema instead of assuming optional columns exist.
        hidden = tuple(sorted(HIDDEN_AUDIT_ACTIONS))
        hidden_placeholders = ",".join(["%s"] * len(hidden))
        cursor.execute(
            f"SELECT * FROM audit_logs WHERE COALESCE(action, '') NOT IN ({hidden_placeholders}) "
            "ORDER BY created_at DESC, log_id DESC LIMIT %s",
            (*hidden, limit),
        )
        raw_logs = cursor.fetchall()

        user_names = {}
        user_ids = sorted({row.get("user_id") for row in raw_logs if row.get("user_id") is not None})
        if user_ids:
            try:
                placeholders = ",".join(["%s"] * len(user_ids))
                cursor.execute(
                    f"SELECT user_id, name FROM users WHERE user_id IN ({placeholders})",
                    tuple(user_ids),
                )
                user_names = {row["user_id"]: row.get("name") for row in cursor.fetchall()}
            except Exception as user_error:
                # User names are helpful but should never make audit history
                # unavailable if a local demo schema differs.
                print("AUDIT USER LOOKUP WARNING:", user_error)
                user_names = {}

        logs = []
        for row in raw_logs:
            details = row.get("details")
            if isinstance(details, str):
                try:
                    details = json.loads(details)
                except Exception:
                    details = {}
            if not isinstance(details, dict):
                details = {}

            status = str(details.get("status") or row.get("status") or "").upper().strip()
            # Older PAWS audit rows do not have a dedicated status column and
            # some historical rows were written without a status in details.
            # Infer a useful display status from the action so the UI does not
            # incorrectly show successful actions as INFO.
            if status not in {"SUCCESS", "FAILED", "INFO"}:
                status = ""
            if not status:
                action_name = str(row.get("action") or "").upper()
                if action_name.endswith("_SUCCESS") or action_name in {
                    "LOGIN", "LOGOUT", "VIEW_CASE", "DOWNLOAD_REPORT",
                    "PRINT_REPORT", "EXPORT_AUDIT_LOG", "ALERT_REVIEW",
                    "CASE_UPDATE", "CASE_STATUS_CHANGED", "VICTIM_VIEW",
                    "VICTIM_UPDATE", "SUPPORT_UPDATE"
                }:
                    status = "SUCCESS"
                elif "FAIL" in action_name or action_name.endswith("_ERROR"):
                    status = "FAILED"
                else:
                    status = "INFO"

            description = str(
                details.get("description")
                or details.get("message")
                or row.get("action")
                or "Officer action recorded."
            )

            created_at = row.get("created_at")
            if created_at:
                created_at = created_at.isoformat()

            user_id = row.get("user_id")
            logs.append({
                "audit_id": row.get("log_id"),
                "officer_id": user_id,
                "officer_name": user_names.get(user_id) or ("System" if user_id is None else f"Officer #{user_id}"),
                "action_role": row.get("action_role") or "OFFICER",
                "action": row.get("action") or "VIEW",
                "entity_type": row.get("entity_type") or "SYSTEM",
                "entity_id": row.get("entity_id"),
                "victim_id": row.get("victim_id"),
                "case_id": row.get("case_id"),
                "details": details,
                "ip_address": row.get("ip_address"),
                "created_at": created_at,
                "description": description,
                "status": status,
            })

        cursor.execute(
            f"SELECT COUNT(*) AS total FROM audit_logs WHERE COALESCE(action, '') NOT IN ({hidden_placeholders})",
            hidden,
        )
        total = cursor.fetchone()["total"]

        cursor.execute(
            f"SELECT COUNT(*) AS today FROM audit_logs "
            f"WHERE DATE(created_at) = CURDATE() AND COALESCE(action, '') NOT IN ({hidden_placeholders})",
            hidden,
        )
        today = cursor.fetchone()["today"]

        cursor.execute(
            f"SELECT COUNT(*) AS case_activity FROM audit_logs "
            f"WHERE entity_type IN ('CASE', 'VICTIM', 'ALERT') AND COALESCE(action, '') NOT IN ({hidden_placeholders})",
            hidden,
        )
        case_activity = cursor.fetchone()["case_activity"]

        # Successful entries are counted from the returned, meaningful events.
        successful = sum(1 for row in logs if row.get("status") == "SUCCESS")

        return jsonify({
            "logs": logs,
            "summary": {
                "total": total,
                "today": today,
                "case_activity": case_activity,
                "successful": successful,
            },
        }), 200

    except Exception as error:
        print("AUDIT LOG ERROR:", error)
        return jsonify({"error": f"Could not retrieve audit logs: {error}"}), 500

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@officer_bp.route("/audit-logs", methods=["POST"])
@token_required
@role_required("OFFICER")
def create_audit_log():
    """Record an authorised officer action."""
    data = request.get_json(silent=True) or {}

    action = str(data.get("action", "VIEW")).strip()[:100] or "VIEW"
    entity_type = str(data.get("entity_type", "SYSTEM")).strip()[:50] or "SYSTEM"
    entity_id = str(data.get("entity_id", "")).strip()[:100] or None
    description = str(data.get("description", "Officer action recorded.")).strip()[:500]
    status = str(data.get("status", "SUCCESS")).strip().upper()[:20] or "SUCCESS"
    if status not in {"SUCCESS", "FAILED", "INFO"}:
        status = "INFO"

    connection = None
    try:
        connection = get_db_connection()
        insert_audit_log(
            connection,
            user_id=request.user.get("user_id"),
            action_role=request.user.get("role", "OFFICER"),
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            status=status,
            ip_address=request.remote_addr,
        )
        return jsonify({"message": "Audit event recorded"}), 201
    except Exception as error:
        print("CREATE AUDIT LOG ERROR:", error)
        return jsonify({"error": f"Could not record audit event: {error}"}), 500
    finally:
        if connection and connection.is_connected():
            connection.close()


# =========================================================
# GET ALL VICTIMS
# =========================================================

@officer_bp.route("/victims", methods=["GET"])
@token_required
@role_required("OFFICER")
def get_victims():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                v.victim_id,
                v.victim_code,
                v.age,
                v.gender,
                v.preferred_language,
                v.safety_status,
                v.created_at
            FROM victims v
            ORDER BY v.created_at DESC
        """)

        victims = cursor.fetchall()

        return jsonify({
            "count": len(victims),
            "victims": victims
        }), 200

    except Exception as error:

        print("GET VICTIMS ERROR:", error)

        return jsonify({
            "error": "Could not retrieve victims"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
            # =========================================================
# VICTIM DETAIL
# =========================================================

@officer_bp.route("/victims/<int:victim_id>", methods=["GET"])
@token_required
@role_required("OFFICER")
def get_victim_detail(victim_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # VICTIM INFORMATION
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                victim_id,
                victim_code,
                age,
                gender,
                preferred_language,
                safety_status,
                created_at
            FROM victims
            WHERE victim_id = %s
        """, (victim_id,))

        victim = cursor.fetchone()

        if not victim:
            return jsonify({
                "error": "Victim not found"
            }), 404

        # -------------------------------------------------
        # DISTRESS HISTORY
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                d.score_id,
                d.checkin_id,
                d.distress_index,
                d.risk_level,
                d.fear_score,
                d.stress_score,
                d.negative_emotion_score,
                d.behaviour_score,
                d.explanation,
                d.created_at
            FROM distress_scores d
            WHERE d.victim_id = %s
            ORDER BY d.created_at ASC
        """, (victim_id,))

        distress_history = cursor.fetchall()

        # -------------------------------------------------
        # CASES
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                case_id,
                case_number,
                case_type,
                current_stage,
                case_status,
                created_at
            FROM cases
            WHERE victim_id = %s
            ORDER BY created_at DESC
        """, (victim_id,))

        cases = cursor.fetchall()

        # -------------------------------------------------
        # CURRENT / LATEST DISTRESS
        # -------------------------------------------------

        latest_distress = None

        if distress_history:
            latest_distress = distress_history[-1]

        # -------------------------------------------------
        # TREND
        # -------------------------------------------------

        if len(distress_history) >= 2:

            first_score = float(
                distress_history[0]["distress_index"]
            )

            latest_score = float(
                distress_history[-1]["distress_index"]
            )

            change = latest_score - first_score

            if change >= 10:
                trend = "WORSENING"
            elif change <= -10:
                trend = "IMPROVING"
            else:
                trend = "STABLE"

        else:

            change = 0
            trend = "INSUFFICIENT_DATA"

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({
            "victim": victim,

            "latest_distress": latest_distress,

            "trend": {
                "direction": trend,
                "change": round(change, 2)
            },

            "distress_history": distress_history,

            "cases": cases

        }), 200

    except Exception as error:

        print("VICTIM DETAIL ERROR:", error)

        return jsonify({
            "error": "Could not retrieve victim details"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()