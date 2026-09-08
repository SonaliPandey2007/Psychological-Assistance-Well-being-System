from flask import Blueprint, jsonify, request

from database.db import get_db_connection
from routes.auth import token_required, role_required


officer_bp = Blueprint(
    "officer",
    __name__,
    url_prefix="/api/officer"
)


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