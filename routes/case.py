from flask import Blueprint, request, jsonify

from database.db import get_db_connection


case_bp = Blueprint(
    "case",
    __name__,
    url_prefix="/api/cases"
)


VALID_STAGES = [
    "COMPLAINT",
    "INVESTIGATION",
    "TRIAL",
    "COMPENSATION",
    "REHABILITATION"
]


# =========================================================
# CREATE CASE
# =========================================================

@case_bp.route("", methods=["POST"])
def create_case():

    data = request.get_json() or {}

    victim_id = data.get("victim_id")
    case_number = data.get("case_number")
    case_type = data.get("case_type")
    current_stage = data.get("current_stage", "COMPLAINT")

    assigned_officer = data.get("assigned_officer")
    assigned_counsellor = data.get("assigned_counsellor")

    if not victim_id or not case_number:
        return jsonify({
            "error": "victim_id and case_number are required"
        }), 400

    if current_stage not in VALID_STAGES:
        return jsonify({
            "error": "Invalid case stage"
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check victim
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

        # Create case
        cursor.execute(
            """
            INSERT INTO cases
            (
                victim_id,
                case_number,
                case_type,
                current_stage,
                assigned_officer,
                assigned_counsellor
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                victim_id,
                case_number,
                case_type,
                current_stage,
                assigned_officer,
                assigned_counsellor
            )
        )

        case_id = cursor.lastrowid

        # Create first timeline event
        cursor.execute(
            """
            INSERT INTO case_events
            (
                case_id,
                event_type,
                description
            )
            VALUES (%s, %s, %s)
            """,
            (
                case_id,
                current_stage,
                f"Case created at {current_stage} stage"
            )
        )

        connection.commit()

        return jsonify({
            "message": "Case created successfully",
            "case_id": case_id,
            "victim_id": victim_id,
            "case_number": case_number,
            "current_stage": current_stage
        }), 201

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print("CREATE CASE ERROR:", error)

        return jsonify({
            "error": "Could not create case"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# UPDATE CASE STAGE
# =========================================================

@case_bp.route("/<int:case_id>/stage", methods=["PUT"])
def update_case_stage(case_id):

    data = request.get_json() or {}

    new_stage = data.get("current_stage")

    if new_stage not in VALID_STAGES:
        return jsonify({
            "error": "Invalid case stage"
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get current stage
        cursor.execute(
            """
            SELECT current_stage
            FROM cases
            WHERE case_id = %s
            """,
            (case_id,)
        )

        case = cursor.fetchone()

        if not case:
            return jsonify({
                "error": "Case not found"
            }), 404

        old_stage = case["current_stage"]

        # Update stage
        cursor.execute(
            """
            UPDATE cases
            SET current_stage = %s
            WHERE case_id = %s
            """,
            (new_stage, case_id)
        )

        # Add timeline event
        cursor.execute(
            """
            INSERT INTO case_events
            (
                case_id,
                event_type,
                description
            )
            VALUES (%s, %s, %s)
            """,
            (
                case_id,
                new_stage,
                f"Case stage changed from {old_stage} to {new_stage}"
            )
        )

        connection.commit()

        return jsonify({
            "message": "Case stage updated successfully",
            "case_id": case_id,
            "previous_stage": old_stage,
            "current_stage": new_stage
        }), 200

    except Exception as error:

        if connection and connection.is_connected():
            connection.rollback()

        print("UPDATE STAGE ERROR:", error)

        return jsonify({
            "error": "Could not update case stage"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# GET CASE DETAILS
# =========================================================

@case_bp.route("/<int:case_id>", methods=["GET"])
def get_case(case_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                c.case_id,
                c.case_number,
                c.case_type,
                c.current_stage,
                c.case_status,
                c.created_at,

                v.victim_id,
                v.victim_code,
                v.preferred_language,
                v.safety_status

            FROM cases c

            JOIN victims v
                ON c.victim_id = v.victim_id

            WHERE c.case_id = %s
            """,
            (case_id,)
        )

        case = cursor.fetchone()

        if not case:
            return jsonify({
                "error": "Case not found"
            }), 404

        return jsonify(case), 200

    except Exception as error:

        print("GET CASE ERROR:", error)

        return jsonify({
            "error": "Could not retrieve case"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# GET CASE TIMELINE
# =========================================================

@case_bp.route("/<int:case_id>/timeline", methods=["GET"])
def get_case_timeline(case_id):

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Check case
        cursor.execute(
            """
            SELECT case_id, case_number, current_stage
            FROM cases
            WHERE case_id = %s
            """,
            (case_id,)
        )

        case = cursor.fetchone()

        if not case:
            return jsonify({
                "error": "Case not found"
            }), 404

        # Get timeline events
        cursor.execute(
            """
            SELECT
                event_id,
                event_type,
                description,
                event_date,
                created_by
            FROM case_events
            WHERE case_id = %s
            ORDER BY event_date ASC
            """,
            (case_id,)
        )

        events = cursor.fetchall()

        return jsonify({
            "case_id": case["case_id"],
            "case_number": case["case_number"],
            "current_stage": case["current_stage"],
            "timeline": events
        }), 200

    except Exception as error:

        print("TIMELINE ERROR:", error)

        return jsonify({
            "error": "Could not retrieve timeline"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()