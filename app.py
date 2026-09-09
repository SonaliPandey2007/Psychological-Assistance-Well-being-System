from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

from routes.victim import victim_bp
from database.db import get_db_connection
from routes.case import case_bp
from routes.auth import auth_bp
from routes.protected import protected_bp
from routes.officer import officer_bp
from routes.counsellor import counsellor_bp


app = Flask(__name__)

CORS(app)


# ==========================================
# REGISTER BLUEPRINTS
# ==========================================

app.register_blueprint(victim_bp)
app.register_blueprint(case_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(officer_bp)
app.register_blueprint(protected_bp)
app.register_blueprint(counsellor_bp)


# ==========================================
# SERVE FRONTEND
# ==========================================

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend")
    return send_from_directory(frontend_path, filename)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return "PAWS Backend is Running 🐾"


# ==========================================
# TEST DATABASE
# ==========================================

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


# ==========================================
# HEALTH
# ==========================================

@app.route("/health")
def health():

    return jsonify({
        "system": "PAWS",
        "status": "online"
    })


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5000
    )