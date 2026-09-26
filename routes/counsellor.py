from flask import Blueprint, request, jsonify

from database.db import get_db_connection
from database.audit import log_audit
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
        v.victim_id,
        v.user_id,
        v.victim_code,
        v.age,
        v.gender,
        v.preferred_language,
        v.safety_status,
        v.created_at,
        u.name AS victim_name,
        u.email AS victim_email
    FROM victims v
    LEFT JOIN users u
        ON v.user_id = u.user_id
    WHERE v.victim_id = %s
""", (victim_id,))

        victim = cursor.fetchone()

        if not victim:
            return jsonify({
                "error": "Victim not found"
            }), 404

        log_audit(
            user_id=request.user["user_id"],
            action_role="COUNSELLOR",
            action="VICTIM_VIEW",
            entity_type="VICTIM",
            entity_id=str(victim_id),
            victim_id=victim_id,
            description=f"Counsellor viewed victim profile {victim_id}.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

        # -------------------------------------------------
        # DISTRESS HISTORY
        # -------------------------------------------------

        cursor.execute("""
    SELECT
        ds.score_id,
        ds.checkin_id,
        ds.distress_index,
        ds.risk_level,
        ds.fear_score,
        ds.stress_score,
        ds.anxiety_score,
        ds.negative_emotion_score,
        ds.behaviour_score,
        ds.explanation,
        ds.created_at,
        ci.engagement_score
    FROM distress_scores ds
    LEFT JOIN check_ins ci
        ON ds.checkin_id = ci.checkin_id
    WHERE ds.victim_id = %s
    ORDER BY ds.created_at ASC
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
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT victim_id
            FROM alerts
            WHERE alert_id = %s
        """, (alert_id,))
        alert = cursor.fetchone()

        if not alert:
            return jsonify({"error": "Alert not found"}), 404

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

        log_audit(
            user_id=request.user["user_id"],
            action_role="COUNSELLOR",
            action="SOS_REVIEWED",
            entity_type="ALERT",
            entity_id=str(alert_id),
            victim_id=alert.get("victim_id"),
            description=f"Counsellor reviewed SOS alert {alert_id}.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

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

        log_audit(
            user_id=request.user["user_id"],
            action_role="COUNSELLOR",
            action="INTERVENTION_RECORDED",
            entity_type="INTERVENTION",
            entity_id=str(intervention_id),
            victim_id=victim_id,
            description=f"Counsellor recorded an intervention for victim {victim_id}.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

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

        log_audit(
            user_id=request.user["user_id"],
            action_role="COUNSELLOR",
            action="VIEW_INTERVENTIONS",
            entity_type="INTERVENTION_HISTORY",
            entity_id=str(victim_id),
            victim_id=victim_id,
            description=f"Counsellor viewed intervention history for victim {victim_id}.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

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

@counsellor_bp.route("/followups", methods=["GET"])
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
                i.intervention_id,
                i.victim_id,
                v.victim_code,
                i.alert_id,
                i.intervention_type,
                i.notes,
                i.outcome,
                i.follow_up_date,
                i.follow_up_status,
                i.created_at,
                d.distress_index,
                d.risk_level
            FROM interventions i
            JOIN victims v
                ON i.victim_id = v.victim_id
            LEFT JOIN distress_scores d
                ON d.score_id = (
                    SELECT MAX(d2.score_id)
                    FROM distress_scores d2
                    WHERE d2.victim_id = i.victim_id
                )
            WHERE i.follow_up_date IS NOT NULL
              AND i.follow_up_status = 'SCHEDULED'
            ORDER BY i.follow_up_date ASC
        """)

        followups = cursor.fetchall()

        log_audit(
            user_id=request.user["user_id"],
            action_role="COUNSELLOR",
            action="VIEW_FOLLOWUPS",
            entity_type="FOLLOWUP",
            entity_id=None,
            description="Counsellor viewed scheduled follow-ups.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

        return jsonify({
            "followups": followups,
            "count": len(followups)
        }), 200

    except Exception as error:
        print("FOLLOWUPS ERROR:", error)
        return jsonify({
            "error": "Could not load follow-ups"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


@counsellor_bp.route(
    "/followups/<int:intervention_id>/complete",
    methods=["PUT"]
)
@token_required
@role_required("COUNSELLOR")
def complete_followup(intervention_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE interventions
            SET follow_up_status = 'COMPLETED'
            WHERE intervention_id = %s
              AND follow_up_status = 'SCHEDULED'
        """, (intervention_id,))

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Follow-up not found or already completed"
            }), 404

        connection.commit()

        followup_victim_id = None
        try:
            cursor.execute(
                "SELECT victim_id FROM interventions WHERE intervention_id = %s",
                (intervention_id,)
            )
            followup = cursor.fetchone()
            followup_victim_id = (followup or {}).get("victim_id") if isinstance(followup, dict) else None
        except Exception:
            followup_victim_id = None

        log_audit(
            user_id=request.user["user_id"],
            action_role="COUNSELLOR",
            action="FOLLOWUP_COMPLETED",
            entity_type="INTERVENTION",
            entity_id=str(intervention_id),
            victim_id=followup_victim_id,
            description=f"Counsellor completed follow-up {intervention_id}.",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

        return jsonify({
            "message": "Follow-up marked as completed",
            "intervention_id": intervention_id,
            "follow_up_status": "COMPLETED"
        }), 200

    except Exception as error:
        if connection and connection.is_connected():
            connection.rollback()

        print("COMPLETE FOLLOWUP ERROR:", error)

        return jsonify({
            "error": "Could not complete follow-up"
        }), 500

    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

@counsellor_bp.route(
    "/messages/<int:victim_id>",
    methods=["GET"]
)
@token_required
@role_required("COUNSELLOR")
def get_messages(victim_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor(
            dictionary=True
        )

        counsellor_id = request.user["user_id"]

        cursor.execute("""
            SELECT
                m.message_id,
                m.sender_id,
                m.receiver_id,
                m.message,
                m.is_read,
                m.created_at,
                sender.name AS sender_name
            FROM messages m
            JOIN users sender
                ON m.sender_id = sender.user_id
            WHERE
                (
                    m.sender_id = %s
                    AND m.receiver_id = (
                        SELECT user_id
                        FROM victims
                        WHERE victim_id = %s
                    )
                )
                OR
                (
                    m.receiver_id = %s
                    AND m.sender_id = (
                        SELECT user_id
                        FROM victims
                        WHERE victim_id = %s
                    )
                )
            ORDER BY m.created_at ASC
        """, (
            counsellor_id,
            victim_id,
            counsellor_id,
            victim_id
        ))

        messages = cursor.fetchall()

        # Mark victim messages as read
        cursor.execute("""
            UPDATE messages
            SET is_read = TRUE
            WHERE receiver_id = %s
              AND sender_id = (
                  SELECT user_id
                  FROM victims
                  WHERE victim_id = %s
              )
              AND is_read = FALSE
        """, (
            counsellor_id,
            victim_id
        ))

        connection.commit()

        return jsonify({
            "victim_id": victim_id,
            "messages": messages
        }), 200

    except Exception as error:

        print(
            "GET MESSAGES ERROR:",
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

@counsellor_bp.route(
    "/messages",
    methods=["POST"]
)
@token_required
@role_required("COUNSELLOR")
def send_message():

    connection = None
    cursor = None

    try:

        data = request.get_json() or {}

        victim_id = data.get(
            "victim_id"
        )

        message = (
            data.get("message") or ""
        ).strip()

        if not victim_id:
            return jsonify({
                "error": "victim_id is required"
            }), 400

        if not message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400

        connection = get_db_connection()

        cursor = connection.cursor()

        counsellor_id = request.user[
            "user_id"
        ]

        # Find victim's user account
        cursor.execute("""
            SELECT user_id
            FROM victims
            WHERE victim_id = %s
        """, (
            victim_id,
        ))

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim not found"
            }), 404

        victim_user_id = victim[0]

        cursor.execute("""
            INSERT INTO messages
            (
                sender_id,
                receiver_id,
                message
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
        """, (
            counsellor_id,
            victim_user_id,
            message
        ))

        connection.commit()

        message_id = cursor.lastrowid

        return jsonify({
            "message": "Message sent successfully",
            "message_id": message_id
        }), 201

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print(
            "SEND MESSAGE ERROR:",
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

@counsellor_bp.route("/video-sessions", methods=["POST"])
@token_required
@role_required("COUNSELLOR")
def create_video_session():

    connection = None
    cursor = None

    try:

        data = request.get_json() or {}

        victim_id = data.get("victim_id")

        if not victim_id:
            return jsonify({
                "error": "victim_id is required"
            }), 400

        connection = get_db_connection()

        cursor = connection.cursor(dictionary=True)

        counsellor_id = request.user["user_id"]

        # Verify victim exists
        cursor.execute("""
            SELECT
                victim_id,
                user_id,
                victim_code
            FROM victims
            WHERE victim_id = %s
        """, (victim_id,))

        victim = cursor.fetchone()

        if not victim:

            return jsonify({
                "error": "Victim not found"
            }), 404

        # Generate unique room code
        import uuid

        room_code = (
            "PAWS-Counselling-" +
            str(victim_id) +
            "-" +
            uuid.uuid4().hex[:10]
        )

        cursor.execute("""
            INSERT INTO video_sessions
            (
                victim_id,
                counsellor_id,
                room_code,
                status
            )
            VALUES (%s, %s, %s, 'CREATED')
        """, (
            victim_id,
            counsellor_id,
            room_code
        ))

        connection.commit()

        session_id = cursor.lastrowid

        return jsonify({
            "message": "Video session created successfully",
            "session_id": session_id,
            "victim_id": victim_id,
            "room_code": room_code,
            "room_url": "https://meet.jit.si/" + room_code
        }), 201

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print(
            "CREATE VIDEO SESSION ERROR:",
            error
        )

        return jsonify({
            "error": "Could not create video session"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()

@counsellor_bp.route(
    "/video-sessions/<int:session_id>/end",
    methods=["PUT"]
)
@token_required
@role_required("COUNSELLOR")
def end_video_session(session_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE video_sessions
            SET
                status = 'ENDED',
                ended_at = CURRENT_TIMESTAMP
            WHERE
                session_id = %s
                AND counsellor_id = %s
                AND status != 'ENDED'
        """, (
            session_id,
            request.user["user_id"]
        ))

        if cursor.rowcount == 0:

            return jsonify({
                "error": "Video session not found"
            }), 404

        connection.commit()

        return jsonify({
            "message": "Video session ended successfully",
            "session_id": session_id
        }), 200

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print(
            "END VIDEO SESSION ERROR:",
            error
        )

        return jsonify({
            "error": "Could not end video session"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if (
            connection
            and connection.is_connected()
        ):
            connection.close()