from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
import jwt
import os
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime, timedelta, timezone
from functools import wraps

from database.db import get_db_connection


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