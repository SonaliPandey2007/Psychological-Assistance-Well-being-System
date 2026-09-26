from flask import Blueprint, request, jsonify, after_this_request
from werkzeug.security import check_password_hash
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime, timedelta, timezone
from functools import wraps

from database.db import get_db_connection
from database.audit import log_audit, insert_audit_log, classify_request, request_audit_context


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/api/auth"
)


# =========================================================
# JWT CONFIG
# =========================================================

JWT_SECRET = os.getenv("JWT_SECRET")

JWT_EXPIRATION_HOURS = 8


# =========================================================
# LOGIN
# =========================================================

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json() or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    connection = None
    cursor = None

    try:

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                user_id,
                name,
                email,
                password_hash,
                role
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        # Verify password
        if not check_password_hash(
            user["password_hash"],
            password
        ):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        # Create JWT
        payload = {
            "user_id": user["user_id"],
            "name": user["name"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc)
                   + timedelta(hours=JWT_EXPIRATION_HOURS)
        }

        token = jwt.encode(
            payload,
            JWT_SECRET,
            algorithm="HS256"
        )

        # Record successful sign-in for every PAWS role.
        # Logging is best-effort and must never break authentication.
        log_audit(
            user_id=user["user_id"],
            action_role=user["role"],
            action="LOGIN_SUCCESS",
            entity_type="AUTH",
            entity_id=str(user["user_id"]),
            description=f"{user['role'].title()} {user['name']} signed in",
            status="SUCCESS",
            ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
        )

        return jsonify({
            "message": "Login successful",
            "token": token,
            "user": {
                "user_id": user["user_id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except Exception as error:

        print("LOGIN ERROR:", error)

        return jsonify({
            "error": "Login failed"
        }), 500

    finally:

        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


# =========================================================
# TOKEN VERIFICATION
# =========================================================

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):

            token = auth_header.split(" ", 1)[1]

        if not token:
            return jsonify({
                "error": "Authentication token required"
            }), 401

        try:

            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=["HS256"]
            )

            request.user = payload

        except jwt.ExpiredSignatureError:

            return jsonify({
                "error": "Token has expired"
            }), 401

        except jwt.InvalidTokenError:

            return jsonify({
                "error": "Invalid authentication token"
            }), 401

        # Automatically audit meaningful actions performed by every authenticated role.
        # Navigation/viewing the dashboard and audit endpoint are intentionally excluded
        # to avoid creating repetitive noise.
        metadata = classify_request(request.path, request.method)
        if metadata:
            @after_this_request
            def _audit_authenticated_action(response):
                try:
                    enriched = request_audit_context(request, response, metadata)
                    connection = get_db_connection()
                    details = {
                        "description": metadata.get("description"),
                        "status": enriched.get("status"),
                        "http_status": enriched.get("response_status"),
                    }
                    if enriched.get("details_alert_id") is not None:
                        details["alert_id"] = enriched["details_alert_id"]
                    insert_audit_log(
                        connection,
                        user_id=request.user.get("user_id"),
                        action_role=request.user.get("role", "SYSTEM"),
                        action=enriched["action"],
                        entity_type=enriched.get("entity_type"),
                        entity_id=str(enriched["entity_id"]) if enriched.get("entity_id") is not None else None,
                        victim_id=enriched.get("victim_id"),
                        case_id=None,
                        description=enriched.get("description", "PAWS action recorded."),
                        status=enriched.get("status", "INFO"),
                        details=details,
                        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
                    )
                    connection.close()
                except Exception as audit_error:
                    print("GLOBAL AUDIT WARNING:", audit_error)
                return response

        return f(*args, **kwargs)

    return decorated


# =========================================================
# ROLE CHECK
# =========================================================

def role_required(*allowed_roles):

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            user = getattr(request, "user", None)

            if not user:
                return jsonify({
                    "error": "Authentication required"
                }), 401

            if user.get("role") not in allowed_roles:

                return jsonify({
                    "error": "Access denied",
                    "required_roles": allowed_roles,
                    "your_role": user.get("role")
                }), 403

            return f(*args, **kwargs)

        return decorated

    return decorator
# =========================================================
# CURRENT USER
# =========================================================

@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user():

    return jsonify({
        "message": "Authenticated successfully",
        "user": request.user
    }), 200

# =========================================================
# LOGOUT (JWT IS STATELESS — CLIENT REMOVES TOKEN)
# =========================================================

@auth_bp.route("/logout", methods=["POST"])
@token_required
def logout():
    user = getattr(request, "user", {})

    log_audit(
        user_id=user.get("user_id"),
        action_role=user.get("role", "SYSTEM"),
        action="LOGOUT",
        entity_type="AUTH",
        entity_id=str(user.get("user_id")) if user.get("user_id") is not None else None,
        description=f"{user.get('role', 'User').title()} {user.get('name', 'User')} signed out",
        status="SUCCESS",
        ip_address=request.headers.get("X-Forwarded-For", request.remote_addr),
    )

    return jsonify({
        "message": "Logout recorded"
    }), 200
