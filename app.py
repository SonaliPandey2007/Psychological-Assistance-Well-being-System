from routes.victim import victim_bp
from flask import Flask, jsonify, send_from_directory, request, redirect, session, url_for
from flask_cors import CORS
from database.db import get_db_connection
from routes.case import case_bp
from routes.auth import auth_bp
from routes.protected import protected_bp
from routes.officer import officer_bp
from routes.counsellor import counsellor_bp

app = Flask(__name__)
CORS(app)
app.register_blueprint(victim_bp)
app.register_blueprint(case_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(officer_bp)
app.register_blueprint(protected_bp)
app.register_blueprint(counsellor_bp)


@app.route("/")
def home():
    return send_from_directory("frontend", "index.html")

@app.route("/victim-login")
def victim_login():
    return send_from_directory("frontend/victim", "login.html")


@app.route("/counsellor-login")
def counsellor_login():
    return send_from_directory("frontend/counsellor", "login.html")

@app.route("/officer-login")
def officer_login():
    return send_from_directory("frontend/officer", "login.html")


@app.route("/test-db")
def test_db():
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")

        database_name = cursor.fetchone()[0]

        cursor.close()
        connection.close()

        return f"Database connected successfully: {database_name}"

    except Exception as error:
        return f"Database connection failed: {error}", 500


@app.route("/health")
def health():
    return jsonify({
        "system": "PAWS",
        "status": "online"
    })

@app.route("/victim/dashboard")
def victim_dashboard():
    return send_from_directory("frontend/victim", "dashboard.html")



@app.route("/victim/checkin")
def victim_checkin():
    return send_from_directory("frontend/victim", "checkin.html")


@app.route("/counsellor/dashboard")
def counsellor_dashboard_page():
    return send_from_directory(
        "frontend/counsellor",
        "dashboard.html"
    )

@app.route("/victim/audio/<path:filename>")
def victim_audio(filename):
    return send_from_directory(
        "frontend/victim/assets/audio",
        filename
    )

@app.route("/victim/yoga/<path:filename>")
def victim_yoga(filename):
    return send_from_directory(
        "frontend/victim/assets/yoga",
        filename
    )


@app.route("/officer/dashboard")
def officer_dashboard():
    return send_from_directory(
        "frontend/officer",
        "officer_dashboard.html"
    )


if __name__ == "__main__":
    app.run(debug=True)