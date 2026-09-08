from flask import Blueprint, jsonify, request

from routes.auth import token_required, role_required


protected_bp = Blueprint(
    "protected",
    __name__,
    url_prefix="/api"
)


# =========================================================
# OFFICER AREA
# =========================================================

@protected_bp.route("/officer/dashboard", methods=["GET"])
@token_required
@role_required("OFFICER")
def officer_dashboard():

    return jsonify({
        "message": "Officer access granted",
        "user": request.user,
        "dashboard": "OFFICER"
    }), 200


# =========================================================
# COUNSELLOR AREA
# =========================================================

@protected_bp.route("/counsellor/dashboard", methods=["GET"])
@token_required
@role_required("COUNSELLOR")
def counsellor_dashboard():

    return jsonify({
        "message": "Counsellor access granted",
        "user": request.user,
        "dashboard": "COUNSELLOR"
    }), 200


# =========================================================
# VICTIM AREA
# =========================================================

@protected_bp.route("/victim/dashboard", methods=["GET"])
@token_required
@role_required("VICTIM")
def victim_dashboard():

    return jsonify({
        "message": "Victim access granted",
        "user": request.user,
        "dashboard": "VICTIM"
    }), 200