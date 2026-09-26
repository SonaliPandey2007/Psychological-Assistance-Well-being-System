from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from database.db import get_db_connection
from database.audit import log_audit
from ai.distress_engine import analyze_checkin, calculate_trend
from routes.auth import token_required, role_required


victim_bp = Blueprint(
    "victim",
    __name__,
    url_prefix="/api/victims"
)


# =========================================================
# CREATE VICTIM
# =========================================================

@victim_bp.route("", methods=["POST"])
def create_victim():

    data = request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    victim_code = data.get("victim_code")

    age = data.get("age")
    gender = data.get("gender")
    language = data.get("preferred_language", "Hindi")

    if not name or not email or not password or not victim_code:
        return jsonify({
            "error": "name, email, password and victim_code are required"
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor()

        # Securely hash password
        password_hash = generate_password_hash(password)

        # ---------------------------------------------
        # Create user
        # ---------------------------------------------

        user_query = """
            INSERT INTO users
            (name, email, password_hash, role)
            VALUES (%s, %s, %s, 'VICTIM')
        """

        cursor.execute(
            user_query,
            (name, email, password_hash)
        )

        user_id = cursor.lastrowid

        # ---------------------------------------------
        # Create victim profile
        # ---------------------------------------------

        victim_query = """
            INSERT INTO victims
            (user_id, victim_code, age, gender, preferred_language)
            VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            victim_query,
            (
                user_id,
                victim_code,
                age,
                gender,
                language
            )
        )

        victim_id = cursor.lastrowid

        connection.commit()

        return jsonify({
            "message": "Victim created successfully",
            "victim_id": victim_id,
            "victim_code": victim_code
        }), 201

    except Exception as error:

        print("CREATE VICTIM ERROR:", error)

        if connection and connection.is_connected():
            connection.rollback()

        return jsonify({
            "error": "Could not create victim"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# VICTIM CHECK-IN
# =========================================================

@victim_bp.route("/<int:victim_id>/check-in", methods=["POST"])
def submit_checkin(victim_id):

    data = request.get_json() or {}

    case_id = data.get("case_id")

    mood_score = data.get("mood_score")
    safety_score = data.get("safety_score")
    stress_level = data.get("stress_level")

    text_response = data.get("text_response", "")

    engagement_score = data.get("engagement_score", 50)

    # ---------------------------------------------
    # Validate required values
    # ---------------------------------------------

    if mood_score is None:
        return jsonify({
            "error": "mood_score is required"
        }), 400

    if safety_score is None:
        return jsonify({
            "error": "safety_score is required"
        }), 400

    if stress_level is None:
        return jsonify({
            "error": "stress_level is required"
        }), 400

    try:

        mood_score = int(mood_score)
        safety_score = int(safety_score)
        stress_level = int(stress_level)
        engagement_score = float(engagement_score)

    except (ValueError, TypeError):

        return jsonify({
            "error": "Scores must be numeric"
        }), 400

    # ---------------------------------------------
    # Validate score ranges
    # ---------------------------------------------

    if not 1 <= mood_score <= 10:
        return jsonify({
            "error": "mood_score must be between 1 and 10"
        }), 400

    if not 1 <= safety_score <= 10:
        return jsonify({
            "error": "safety_score must be between 1 and 10"
        }), 400

    if not 1 <= stress_level <= 10:
        return jsonify({
            "error": "stress_level must be between 1 and 10"
        }), 400

    if not 0 <= engagement_score <= 100:
        return jsonify({
            "error": "engagement_score must be between 0 and 100"
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =================================================
        # CHECK WHETHER VICTIM EXISTS
        # =================================================

        cursor.execute(
            """
            SELECT victim_id
            FROM victims
            WHERE victim_id = %s
            """,
            (victim_id,)
        )

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim not found"
            }), 404

        # =================================================
        # GET PREVIOUS ENGAGEMENT SCORES
        # =================================================

        cursor.execute(
            """
            SELECT engagement_score
            FROM check_ins
            WHERE victim_id = %s
              AND engagement_score IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (victim_id,)
        )

        previous_rows = cursor.fetchall()

        previous_engagements = [
            float(row["engagement_score"])
            for row in previous_rows
        ]

        # =================================================
        # GET PREVIOUS NEGATIVE EMOTION SCORES
        # =================================================

        cursor.execute(
            """
            SELECT negative_emotion_score
            FROM distress_scores
            WHERE victim_id = %s
              AND negative_emotion_score IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (victim_id,)
        )

        previous_emotion_rows = cursor.fetchall()

        previous_negative_scores = [
            float(row["negative_emotion_score"])
            for row in previous_emotion_rows
        ]

        # =================================================
        # RUN PAWS AI ENGINE
        # =================================================

        ai_result = analyze_checkin(
            text=text_response,
            mood_score=mood_score,
            safety_score=safety_score,
            self_report_stress=stress_level,
            current_engagement=engagement_score,
            previous_engagements=previous_engagements,
            previous_negative_scores=previous_negative_scores
        )

        nlp_result = ai_result["nlp"]

        behaviour_score = ai_result["behaviour_score"]

        emotional_change = ai_result["emotional_change"]

        ddi_result = ai_result["ddi"]

        explanation_result = ai_result["explanation"]

        distress_index = ddi_result["distress_index"]

        risk_level = ddi_result["risk_level"]

        # =================================================
        # BUILD EXPLAINABLE AI REASONS
        # =================================================

        reasons = list(
            explanation_result.get("reasons", [])
        )

        # Add self-reported indicators

        if stress_level >= 7:
            reasons.append(
                "High self-reported stress"
            )

        if safety_score <= 4:
            reasons.append(
                "Low self-reported safety"
            )

        if mood_score <= 4:
            reasons.append(
                "Low self-reported mood"
            )

        # Remove duplicate reasons
        reasons = list(dict.fromkeys(reasons))

        # Fallback
        if not reasons:
            reasons.append(
                "No major distress indicators detected"
            )

        explanation = "; ".join(reasons)

        # =================================================
        # SAVE CHECK-IN
        # =================================================

        checkin_query = """
            INSERT INTO check_ins
            (
                victim_id,
                case_id,
                mood_score,
                safety_score,
                stress_level,
                text_response,
                engagement_score
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            checkin_query,
            (
                victim_id,
                case_id,
                mood_score,
                safety_score,
                stress_level,
                text_response,
                engagement_score
            )
        )

        checkin_id = cursor.lastrowid

        # =================================================
        # SAVE DISTRESS SCORE
        # =================================================

        score_query = """
            INSERT INTO distress_scores
            (
                victim_id,
                checkin_id,
                distress_index,
                risk_level,
                fear_score,
                stress_score,
                anxiety_score,
                negative_emotion_score,
                behaviour_score,
                explanation
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(
            score_query,
            (
                victim_id,
                checkin_id,
                distress_index,
                risk_level,
                nlp_result["fear_score"],
                nlp_result["stress_score"],
                nlp_result["anxiety_score"],
                nlp_result["negative_emotion_score"],
                behaviour_score,
                explanation
            )
        )

        score_id = cursor.lastrowid

        # =================================================
        # CREATE HIGH-RISK ALERT
        # =================================================

        alert_created = False

        if risk_level == "HIGH":

            alert_query = """
                INSERT INTO alerts
                (
                    victim_id,
                    score_id,
                    alert_type,
                    severity,
                    message
                )
                VALUES (%s, %s, %s, %s, %s)
            """

            cursor.execute(
                alert_query,
                (
                    victim_id,
                    score_id,
                    "DISTRESS_RISK",
                    "HIGH",
                    "PAWS detected a high distress indicator. Human counsellor review recommended."
                )
            )

            alert_created = True

        # =================================================
        # COMMIT EVERYTHING
        # =================================================

        connection.commit()


        # Link the check-in to the corresponding PAWS user when the local schema supports it.
        checkin_user_id = None
        try:
            cursor.execute("SELECT user_id FROM victims WHERE victim_id = %s", (victim_id,))
            linked_victim = cursor.fetchone() or {}
            checkin_user_id = linked_victim.get("user_id")
        except Exception:
            checkin_user_id = None

        log_audit(
            user_id=checkin_user_id,
            action_role="VICTIM",
            action="CHECKIN_SUBMITTED",
            entity_type="VICTIM",
            entity_id=str(victim_id),
            victim_id=victim_id,
            case_id=case_id,
            description=f"Victim {victim_id} submitted a wellbeing check-in.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )


        # =================================================
        # RETURN AI ANALYSIS
        # =================================================

        return jsonify({

            "message":
                "Check-in analyzed successfully",

            "victim_id":
                victim_id,

            "checkin_id":
                checkin_id,

            "ai_analysis": {

                "fear_score":
                    nlp_result["fear_score"],

                "stress_score":
                    nlp_result["stress_score"],

                "anxiety_score":
                    nlp_result["anxiety_score"],

                "negative_emotion_score":
                    nlp_result["negative_emotion_score"],

                "behaviour_score":
                    behaviour_score,

                "emotional_change":
                    emotional_change,

                "matched_indicators":
                    nlp_result["matched_indicators"]
            },

            "distress_result": {

                "distress_index":
                    distress_index,

                "risk_level":
                    risk_level,

                "explanation":
                    explanation,

                "reasons":
                    reasons
            },

            "alert_created":
                alert_created

        }), 201

    except Exception as error:

        print("CHECK-IN ERROR:", error)

        if connection and connection.is_connected():
            connection.rollback()

        return jsonify({
            "error": "Could not process check-in"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# VICTIM WELL-BEING HISTORY
# =========================================================

@victim_bp.route("/<int:victim_id>/history", methods=["GET"])
def get_victim_history(victim_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # ---------------------------------------------
        # Check whether victim exists
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT victim_id, victim_code
            FROM victims
            WHERE victim_id = %s
            """,
            (victim_id,)
        )

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim not found"
            }), 404

        # ---------------------------------------------
        # Get complete history
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT
                ci.checkin_id,
                ci.mood_score,
                ci.safety_score,
                ci.stress_level,
                ci.engagement_score,
                ci.created_at,

                ds.score_id,
                ds.distress_index,
                ds.risk_level,
                ds.fear_score,
                ds.stress_score,
                ds.anxiety_score,
                ds.negative_emotion_score,
                ds.behaviour_score,
                ds.explanation

            FROM check_ins ci

            LEFT JOIN distress_scores ds
                ON ci.checkin_id = ds.checkin_id

            WHERE ci.victim_id = %s

            ORDER BY ci.created_at ASC
            """,
            (victim_id,)
        )

        history = cursor.fetchall()

        # ---------------------------------------------
        # Calculate DDI trend
        # ---------------------------------------------

        ddi_history = [
            float(row["distress_index"])
            for row in history
            if row["distress_index"] is not None
        ]

        trend_result = calculate_trend(
            ddi_history
        )

        # ---------------------------------------------
        # Return history + trend
        # ---------------------------------------------

        return jsonify({

            "victim_id":
                victim["victim_id"],

            "victim_code":
                victim["victim_code"],

            "total_checkins":
                len(history),

            "trend": {

                "status":
                    trend_result["trend"],

                "change":
                    trend_result["change"]
            },

            "history":
                history

        }), 200

    except Exception as error:

        print("HISTORY ERROR:", error)

        return jsonify({
            "error": "Could not retrieve victim history"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# VICTIM DASHBOARD
# =========================================================

@victim_bp.route("/dashboard", methods=["GET"])
@token_required
@role_required("VICTIM")
def victim_dashboard():

    user_id = request.user["user_id"]

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # =================================================
        # FIND VICTIM LINKED TO LOGGED-IN USER
        # =================================================

        cursor.execute(
            """
            SELECT
                victim_id,
                victim_code,
                age,
                gender,
                preferred_language,
                safety_status
            FROM victims
            WHERE user_id = %s
            """,
            (user_id,)
        )

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim profile not found"
            }), 404

        victim_id = victim["victim_id"]

        # =================================================
        # LATEST DISTRESS
        # =================================================

        cursor.execute(
            """
            SELECT
                distress_index,
                risk_level,
                fear_score,
                stress_score,
                anxiety_score,
                negative_emotion_score,
                behaviour_score,
                explanation,
                created_at
            FROM distress_scores
            WHERE victim_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (victim_id,)
        )

        latest_distress = cursor.fetchone()

        # =================================================
        # DISTRESS HISTORY
        # =================================================

        cursor.execute(
            """
            SELECT
                distress_index,
                risk_level,
                created_at
            FROM distress_scores
            WHERE victim_id = %s
            ORDER BY created_at ASC
            """,
            (victim_id,)
        )

        distress_history = cursor.fetchall()

        # =================================================
        # LATEST INTERVENTION
        # =================================================

        cursor.execute(
            """
            SELECT
                intervention_type,
                notes,
                outcome,
                follow_up_date,
                created_at
            FROM interventions
            WHERE victim_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (victim_id,)
        )

        latest_intervention = cursor.fetchone()

        # =================================================
        # CASES
        # =================================================

        cursor.execute(
            """
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
            """,
            (victim_id,)
        )

        cases = cursor.fetchall()

        # =================================================
        # CALCULATE SIMPLE DDI TREND
        # =================================================

        ddi_history = [
            float(row["distress_index"])
            for row in distress_history
            if row["distress_index"] is not None
        ]

        trend_result = calculate_trend(
            ddi_history
        )

        # =================================================
        # RETURN DASHBOARD DATA
        # =================================================

        return jsonify({

            "victim":
                victim,

            "latest_distress":
                latest_distress,

            "trend": {

                "direction":
                    trend_result["trend"],

                "change":
                    trend_result["change"]
            },

            "distress_history":
                distress_history,

            "latest_intervention":
                latest_intervention,

            "cases":
                cases

        }), 200

    except Exception as error:

        print(
            "VICTIM DASHBOARD ERROR:",
            error
        )

        return jsonify({
            "error": "Failed to load victim dashboard"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# VICTIM HELP REQUEST
# =========================================================

@victim_bp.route("/help", methods=["POST"])
@token_required
@role_required("VICTIM")
def request_help():

    user_id = request.user["user_id"]

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # ---------------------------------------------
        # Find victim linked to logged-in user
        # ---------------------------------------------

        cursor.execute(
            """
            SELECT victim_id
            FROM victims
            WHERE user_id = %s
            """,
            (user_id,)
        )

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim profile not found"
            }), 404

        victim_id = victim["victim_id"]

        # ---------------------------------------------
        # Create priority support alert
        # ---------------------------------------------

        cursor.execute(
            """
            INSERT INTO alerts
            (
                victim_id,
                alert_type,
                severity,
                message
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                victim_id,
                "VICTIM_REQUEST",
                "HIGH",
                "Victim has requested immediate support."
            )
        )

        connection.commit()

        return jsonify({

            "message":
                "Support request sent successfully",

            "status":
                "PRIORITY_SUPPORT_REQUESTED"

        }), 201

    except Exception as error:

        print(
            "HELP REQUEST ERROR:",
            error
        )

        if connection and connection.is_connected():
            connection.rollback()

        return jsonify({
            "error": "Failed to send support request"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# VICTIM MESSAGING
# =========================================================

@victim_bp.route("/messages", methods=["GET"])
@token_required
@role_required("VICTIM")
def get_victim_messages():

    connection = None
    cursor = None

    try:

        user_id = request.user["user_id"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Find the victim linked to the logged-in user
        # -------------------------------------------------

        cursor.execute("""
            SELECT victim_id
            FROM victims
            WHERE user_id = %s
        """, (user_id,))

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim profile not found"
            }), 404

        victim_id = victim["victim_id"]

        # -------------------------------------------------
        # Get conversation
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                m.message_id,
                m.sender_id,
                m.receiver_id,
                m.message,
                m.is_read,
                m.created_at,

                sender.name AS sender_name,
                receiver.name AS receiver_name

            FROM messages m

            JOIN users sender
                ON m.sender_id = sender.user_id

            JOIN users receiver
                ON m.receiver_id = receiver.user_id

            WHERE
                (m.sender_id = %s OR m.receiver_id = %s)

            ORDER BY m.created_at ASC
        """, (
            user_id,
            user_id
        ))

        messages = cursor.fetchall()

        # -------------------------------------------------
        # Mark messages received by victim as read
        # -------------------------------------------------

        cursor.execute("""
            UPDATE messages
            SET is_read = TRUE
            WHERE receiver_id = %s
              AND is_read = FALSE
        """, (user_id,))

        connection.commit()

        return jsonify({
            "messages": messages
        }), 200

    except Exception as error:

        print(
            "VICTIM MESSAGES ERROR:",
            error
        )

        return jsonify({
            "error": "Could not load messages"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


@victim_bp.route("/messages", methods=["POST"])
@token_required
@role_required("VICTIM")
def send_victim_message():

    connection = None
    cursor = None

    try:

        data = request.get_json() or {}

        message = (
            data.get("message") or ""
        ).strip()

        if not message:

            return jsonify({
                "error": "Message cannot be empty"
            }), 400

        user_id = request.user["user_id"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Find victim
        # -------------------------------------------------

        cursor.execute("""
            SELECT victim_id
            FROM victims
            WHERE user_id = %s
        """, (user_id,))

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim profile not found"
            }), 404

        victim_id = victim["victim_id"]

        # -------------------------------------------------
        # Find counsellor assigned to this victim
        # -------------------------------------------------

        cursor.execute("""
            SELECT assigned_counsellor
            FROM cases
            WHERE victim_id = %s
              AND assigned_counsellor IS NOT NULL
            ORDER BY created_at DESC
            LIMIT 1
        """, (victim_id,))

        case = cursor.fetchone()

        counsellor_id = (
            case["assigned_counsellor"]
            if case
            else None
        )

        # -------------------------------------------------
        # If no counsellor is assigned, use an available
        # counsellor for the prototype.
        # -------------------------------------------------

        if not counsellor_id:

            cursor.execute("""
                SELECT user_id
                FROM users
                WHERE role = 'COUNSELLOR'
                ORDER BY user_id ASC
                LIMIT 1
            """)

            counsellor = cursor.fetchone()

            if not counsellor:

                return jsonify({
                    "error":
                        "No counsellor is currently available"
                }), 404

            counsellor_id = counsellor["user_id"]

        # -------------------------------------------------
        # Insert message
        # -------------------------------------------------

        cursor.execute("""
            INSERT INTO messages
            (
                sender_id,
                receiver_id,
                message
            )
            VALUES (%s, %s, %s)
        """, (
            user_id,
            counsellor_id,
            message
        ))

        connection.commit()

        message_id = cursor.lastrowid

        return jsonify({
            "message":
                "Message sent successfully",
            "message_id":
                message_id
        }), 201

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print(
            "SEND VICTIM MESSAGE ERROR:",
            error
        )

        return jsonify({
            "error": "Could not send message"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# =========================================================
# VICTIM VIDEO COUNSELLING
# =========================================================

@victim_bp.route("/video-sessions", methods=["GET"])
@token_required
@role_required("VICTIM")
def get_victim_video_session():

    connection = None
    cursor = None

    try:

        user_id = request.user["user_id"]

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # -------------------------------------------------
        # Find victim linked to logged-in user
        # -------------------------------------------------

        cursor.execute("""
            SELECT victim_id
            FROM victims
            WHERE user_id = %s
        """, (user_id,))

        victim = cursor.fetchone()

        if not victim:
            return jsonify({
                "error": "Victim profile not found"
            }), 404

        victim_id = victim["victim_id"]

        # -------------------------------------------------
        # Find latest active video session
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                session_id,
                victim_id,
                counsellor_id,
                room_code,
                status,
                started_at,
                ended_at,
                created_at
            FROM video_sessions
            WHERE victim_id = %s
              AND status != 'ENDED'
            ORDER BY created_at DESC
            LIMIT 1
        """, (victim_id,))

        session = cursor.fetchone()

        if not session:
            return jsonify({
                "session": None
            }), 200

        # -------------------------------------------------
        # Build Jitsi room URL
        # -------------------------------------------------

        session["room_url"] = (
            "https://meet.jit.si/" +
            session["room_code"]
        )

        return jsonify({
            "session": session
        }), 200

    except Exception as error:

        print(
            "VICTIM VIDEO SESSION ERROR:",
            error
        )

        return jsonify({
            "error": "Could not load video session"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()