from routes.victim import victim_bp
from flask import Flask, jsonify
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
    return "PAWS Backend is Running 🐾"


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


if __name__ == "__main__":
    app.run(debug=True)