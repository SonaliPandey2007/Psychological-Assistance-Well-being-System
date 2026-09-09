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
        print("COUNSELLOR DASHBOARD DATA:", alerts, priority_victims)

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
                score_id,
                checkin_id,
                distress_index,
                risk_level,
                fear_score,
                stress_score,
                negative_emotion_score,
                behaviour_score,
                explanation,
                created_at
            FROM distress_scores
            WHERE victim_id = %s
            ORDER BY created_at ASC
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