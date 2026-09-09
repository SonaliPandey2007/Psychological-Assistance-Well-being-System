from flask import Blueprint, request, jsonify

from database.db import get_db_connection
from routes.auth import token_required, role_required


counsellor_bp = Blueprint(
    "counsellor",
    __name__,
    url_prefix="/api/counsellor"
)


# =========================================================
# COUNSELLOR DASHBOARD
# =========================================================

@counsellor_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("COUNSELLOR")
def dashboard():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # HIGH-RISK ALERTS
        # -------------------------------------------------

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
            WHERE a.is_reviewed = FALSE
            ORDER BY
                CASE
                    WHEN a.severity = 'HIGH' THEN 1
                    WHEN a.severity = 'MODERATE' THEN 2
                    ELSE 3
                END,
                a.created_at DESC
        """)

        alerts = cursor.fetchall()

        # -------------------------------------------------
        # HIGH-RISK VICTIMS
        # -------------------------------------------------

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
            WHERE d.risk_level IN ('HIGH', 'MODERATE')
            ORDER BY d.distress_index DESC
        """)

        priority_victims = cursor.fetchall()

        return jsonify({
            "dashboard": "COUNSELLOR",
            "pending_alerts": len(alerts),
            "alerts": alerts,
            "priority_victims": priority_victims
        }), 200

    except Exception as error:

        print("COUNSELLOR DASHBOARD ERROR:", error)

        return jsonify({
            "error": "Could not load counsellor dashboard"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# VICTIM DISTRESS PROFILE
# =========================================================

@counsellor_bp.route(
    "/victims/<int:victim_id>",
    methods=["GET"]
)
@token_required
@role_required("COUNSELLOR")
def victim_profile(victim_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # VICTIM
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

        c.mood_score,
        c.safety_score,
        c.stress_level,
        c.text_response,
        c.engagement_score,

        d.distress_index,
        d.risk_level,
        d.fear_score,
        d.stress_score,
        d.anxiety_score,
        d.negative_emotion_score,
        d.behaviour_score,
        d.explanation,

        d.created_at

    FROM distress_scores d

    LEFT JOIN check_ins c
        ON d.checkin_id = c.checkin_id

    WHERE d.victim_id = %s

    ORDER BY d.created_at ASC
""", (victim_id,))

        history = cursor.fetchall()

        # -------------------------------------------------
        # LATEST SCORE
        # -------------------------------------------------

        latest = history[-1] if history else None

        # -------------------------------------------------
        # TREND
        # -------------------------------------------------

        if len(history) >= 2:

            first = float(history[0]["distress_index"])
            last = float(history[-1]["distress_index"])

            change = last - first

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

        return jsonify({
            "victim": victim,
            "latest_distress": latest,
            "trend": {
                "direction": trend,
                "change": round(change, 2)
            },
            "distress_history": history,
            "cases": cases
        }), 200

    except Exception as error:

        print("COUNSELLOR VICTIM ERROR:", error)

        return jsonify({
            "error": "Could not retrieve victim profile"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# REVIEW ALERT
# =========================================================

@counsellor_bp.route(
    "/alerts/<int:alert_id>/review",
    methods=["PUT"]
)
@token_required
@role_required("COUNSELLOR")
def review_alert(alert_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE alerts
            SET
                is_reviewed = TRUE,
                reviewed_by = %s
            WHERE alert_id = %s
        """, (
            request.user["user_id"],
            alert_id
        ))

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Alert not found"
            }), 404

        connection.commit()

        return jsonify({
            "message": "Alert reviewed successfully",
            "alert_id": alert_id,
            "reviewed_by": request.user["user_id"]
        }), 200

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print("REVIEW ALERT ERROR:", error)

        return jsonify({
            "error": "Could not review alert"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@counsellor_bp.route("/interventions", methods=["POST"])
@token_required
@role_required("COUNSELLOR")
def create_intervention():

    data = request.get_json() or {}

    victim_id = data.get("victim_id")
    alert_id = data.get("alert_id")
    intervention_type = data.get("intervention_type")
    notes = data.get("notes")
    outcome = data.get("outcome")
    follow_up_date = data.get("follow_up_date")

    if not victim_id or not intervention_type:
        return jsonify({
            "error": "victim_id and intervention_type are required"
        }), 400

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO interventions
            (
                victim_id,
                counsellor_id,
                alert_id,
                intervention_type,
                notes,
                outcome,
                follow_up_date
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            victim_id,
            request.user["user_id"],
            alert_id,
            intervention_type,
            notes,
            outcome,
            follow_up_date
        ))

        connection.commit()

        intervention_id = cursor.lastrowid

        return jsonify({
            "message": "Intervention recorded successfully",
            "intervention_id": intervention_id
        }), 201

    except Exception as error:
        print("INTERVENTION ERROR:", error)
        return jsonify({
            "error": "Failed to record intervention"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
@counsellor_bp.route("/victims/<int:victim_id>/interventions", methods=["GET"])
@token_required
@role_required("COUNSELLOR")
def get_interventions(victim_id):

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                i.intervention_id,
                i.victim_id,
                i.counsellor_id,
                i.alert_id,
                i.intervention_type,
                i.notes,
                i.outcome,
                i.follow_up_date,
                i.created_at,
                u.name AS counsellor_name
            FROM interventions i
            JOIN users u
                ON i.counsellor_id = u.user_id
            WHERE i.victim_id = %s
            ORDER BY i.created_at DESC
        """, (victim_id,))

        interventions = cursor.fetchall()

        return jsonify({
            "victim_id": victim_id,
            "interventions": interventions
        }), 200

    except Exception as error:
        print("INTERVENTION HISTORY ERROR:", error)
        return jsonify({
            "error": "Failed to fetch intervention history"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()    

# =========================================================
# UPDATE ALERT STATUS
# =========================================================

@counsellor_bp.route(
    "/api/counsellor/alerts/<int:alert_id>/status",
    methods=["PUT"]
)
@token_required
@role_required("COUNSELLOR")
def update_alert_status(alert_id):

    data = request.get_json() or {}

    status = data.get("status")
    follow_up_date = data.get("follow_up_date")

    allowed_statuses = [
        "Contacted",
        "Counselling",
        "Follow-up",
        "Resolved"
    ]

    if status not in allowed_statuses:
        return jsonify({
            "error": "Invalid status"
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Find alert
        cursor.execute("""
            SELECT
                alert_id,
                victim_id,
                severity,
                message
            FROM alerts
            WHERE alert_id = %s
        """, (alert_id,))

        alert = cursor.fetchone()

        if not alert:
            return jsonify({
                "error": "Alert not found"
            }), 404

        # -------------------------------------------------
        # RESOLVED
        # -------------------------------------------------

        if status == "Resolved":

            cursor.execute("""
                UPDATE alerts
                SET
                    is_reviewed = TRUE,
                    reviewed_by = %s
                WHERE alert_id = %s
            """, (
                request.user["user_id"],
                alert_id
            ))

            connection.commit()

            return jsonify({
                "message": "Alert resolved successfully",
                "alert_id": alert_id,
                "status": "Resolved"
            }), 200

        # -------------------------------------------------
        # FOLLOW-UP
        # -------------------------------------------------

        if status == "Follow-up":

            if not follow_up_date:
                return jsonify({
                    "error": "Follow-up date is required"
                }), 400

            cursor.execute("""
                UPDATE alerts
                SET
                    is_reviewed = FALSE,
                    reviewed_by = %s,
                    message = CONCAT(
                        COALESCE(message, ''),
                        ' | Follow-up scheduled: ',
                        %s
                    )
                WHERE alert_id = %s
            """, (
                request.user["user_id"],
                follow_up_date,
                alert_id
            ))

            connection.commit()

            return jsonify({
                "message": "Follow-up scheduled successfully",
                "alert_id": alert_id,
                "status": "Follow-up",
                "follow_up_date": follow_up_date
            }), 200

        # -------------------------------------------------
        # CONTACTED / COUNSELLING
        # -------------------------------------------------

        cursor.execute("""
            UPDATE alerts
            SET
                reviewed_by = %s
            WHERE alert_id = %s
        """, (
            request.user["user_id"],
            alert_id
        ))

        connection.commit()

        return jsonify({
            "message": "Alert status updated successfully",
            "alert_id": alert_id,
            "status": status
        }), 200

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print("UPDATE ALERT STATUS ERROR:", error)

        return jsonify({
            "error": "Could not update alert status"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()     

# =========================================================
# GET SCHEDULED FOLLOW-UPS
# =========================================================

@counsellor_bp.route(
    "/api/counsellor/followups",
    methods=["GET"]
)
@token_required
@role_required("COUNSELLOR")
def get_followups():

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                a.alert_id,
                a.victim_id,
                v.victim_code,
                a.severity,
                a.message,
                a.created_at
            FROM alerts a
            JOIN victims v
                ON a.victim_id = v.victim_id
            WHERE
                a.is_reviewed = FALSE
                AND a.message LIKE '%Follow-up scheduled:%'
            ORDER BY a.created_at DESC
        """)

        rows = cursor.fetchall()

        followups = []

        for row in rows:

            message = row.get("message") or ""

            follow_up_date = None

            marker = "Follow-up scheduled:"

            if marker in message:

                follow_up_date = (
                    message.split(marker, 1)[1]
                    .strip()
                )

            followups.append({
                "alert_id": row["alert_id"],
                "victim_id": row["victim_id"],
                "victim_code": row["victim_code"],
                "risk_level": row["severity"],
                "follow_up_date": follow_up_date,
                "created_at": row["created_at"]
            })

        return jsonify({
            "followups": followups
        }), 200

    except Exception as error:

        print("FOLLOW-UP ERROR:", error)

        return jsonify({
            "error": "Could not load follow-ups"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()  

# =========================================================
# COMPLETE FOLLOW-UP
# =========================================================

@counsellor_bp.route(
    "/alerts/<int:alert_id>/follow-up/complete",
    methods=["PUT"]
)
@token_required
@role_required("COUNSELLOR")
def complete_followup(alert_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE alerts
            SET
                is_reviewed = TRUE,
                reviewed_by = %s
            WHERE alert_id = %s
        """, (
            request.user["user_id"],
            alert_id
        ))

        if cursor.rowcount == 0:

            return jsonify({
                "error": "Follow-up not found"
            }), 404

        connection.commit()

        return jsonify({
            "message": "Follow-up completed successfully",
            "alert_id": alert_id
        }), 200

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print("COMPLETE FOLLOW-UP ERROR:", error)

        return jsonify({
            "error": "Could not complete follow-up"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()