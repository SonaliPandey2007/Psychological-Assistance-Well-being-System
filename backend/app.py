from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

from datetime import datetime
import os




# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()


# ==========================================
# CREATE FLASK APPLICATION
# ==========================================

app = Flask(__name__)

CORS(app)


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# ==========================================
# INITIALIZE DATABASE
# ==========================================

db = SQLAlchemy(app)


# ==========================================
# DATABASE MODELS
# ==========================================

class Victim(db.Model):

    __tablename__ = "victims"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    victim_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Checkin(db.Model):

    __tablename__ = "checkins"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    victim_id = db.Column(
        db.String(50),
        nullable=False
    )

    mood = db.Column(
        db.String(50),
        nullable=False
    )

    safety = db.Column(
        db.String(20),
        nullable=False
    )

    fear_level = db.Column(
        db.Integer,
        nullable=False
    )

    text_response = db.Column(
        db.Text
    )

    ddi_score = db.Column(
        db.Integer,
        nullable=False
    )

    risk_level = db.Column(
        db.String(20),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Alert(db.Model):

    __tablename__ = "alerts"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    victim_id = db.Column(
        db.String(50),
        nullable=False
    )

    checkin_id = db.Column(
        db.Integer,
        nullable=False
    )

    risk_level = db.Column(
        db.String(20),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    follow_up_date = db.Column(
    db.DateTime,
    nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ==========================================
# SERVE FRONTEND
# ==========================================

@app.route("/frontend/<path:filename>")
def serve_frontend(filename):
    frontend_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "frontend")
    )

    print("FRONTEND PATH:", frontend_path)
    print("REQUESTED FILE:", filename)
    print(
        "FULL FILE PATH:",
        os.path.join(frontend_path, filename)
    )

    return send_from_directory(frontend_path, filename)




# ==========================================
# DDI CALCULATION
# ==========================================

def calculate_ddi(mood, safety, fear_level, text):

    score = 0

    explanations = []


    # --------------------------------------
    # MOOD ANALYSIS
    # --------------------------------------

    mood_scores = {

        "Happy": 0,
        "Okay": 10,
        "Stressed": 25,
        "Sad": 30,
        "Scared": 40

    }


    score += mood_scores.get(mood, 0)


    if mood == "Scared":

        explanations.append(
            "Fear-related emotional indicators detected"
        )

    elif mood in ["Sad", "Stressed"]:

        explanations.append(
            "Negative emotional indicators detected"
        )


    # --------------------------------------
    # SAFETY ANALYSIS
    # --------------------------------------

    if safety == "No":

        score += 30

        explanations.append(
            "Victim reported feeling unsafe"
        )


    # --------------------------------------
    # FEAR LEVEL
    # --------------------------------------

    fear_score = int(fear_level) * 3

    score += fear_score


    if int(fear_level) >= 7:

        explanations.append(
            "High fear or anxiety level reported"
        )


    # --------------------------------------
    # TEXT ANALYSIS
    # --------------------------------------

    distress_keywords = [

        "scared",
        "afraid",
        "unsafe",
        "help",
        "danger",
        "fear",
        "threat",
        "worried",
        "anxious",
        "alone"

    ]


    text = text.lower()


    detected_keywords = []


    for keyword in distress_keywords:

        if keyword in text:

            score += 5

            detected_keywords.append(keyword)


    if detected_keywords:

        explanations.append(

            "Distress-related language detected: " +

            ", ".join(detected_keywords)

        )


    # --------------------------------------
    # LIMIT SCORE TO 100
    # --------------------------------------

    score = min(score, 100)


    # --------------------------------------
    # RISK LEVEL
    # --------------------------------------

    if score >= 70:

        risk_level = "High"

    elif score >= 35:

        risk_level = "Medium"

    else:

        risk_level = "Low"


    return score, risk_level, explanations


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():

    return jsonify({

        "message": "PAWS Backend is Running!",
        "database": "MySQL Connected"

    })


# ==========================================
# CREATE CHECK-IN API
# ==========================================

@app.route("/checkin", methods=["POST"])
def create_checkin():

    data = request.get_json()


    # --------------------------------------
    # VALIDATE DATA
    # --------------------------------------

    required_fields = [

        "victimId",
        "mood",
        "safety",
        "fearLevel"

    ]


    for field in required_fields:

        if field not in data:

            return jsonify({

                "error":

                f"Missing required field: {field}"

            }), 400


    # --------------------------------------
    # GET DATA
    # --------------------------------------

    victim_id = data["victimId"]

    mood = data["mood"]

    safety = data["safety"]

    fear_level = int(data["fearLevel"])

    text_response = data.get("text", "")


    # --------------------------------------
    # CALCULATE DDI
    # --------------------------------------

    ddi_score, risk_level, explanations = calculate_ddi(

        mood,

        safety,

        fear_level,

        text_response

    )


    # --------------------------------------
    # CREATE CHECK-IN
    # --------------------------------------

    new_checkin = Checkin(

        victim_id=victim_id,

        mood=mood,

        safety=safety,

        fear_level=fear_level,

        text_response=text_response,

        ddi_score=ddi_score,

        risk_level=risk_level

    )


    db.session.add(new_checkin)

    db.session.commit()


    # --------------------------------------
    # CREATE HIGH-RISK ALERT
    # --------------------------------------

    alert_created = False


    if risk_level == "High":

        new_alert = Alert(

            victim_id=victim_id,

            checkin_id=new_checkin.id,

            risk_level=risk_level,

            status="Pending"

        )


        db.session.add(new_alert)

        db.session.commit()

        alert_created = True


    # --------------------------------------
    # RESPONSE
    # --------------------------------------

    return jsonify({

        "message":

        "Check-in successfully recorded",

        "ddi_score":

        ddi_score,

        "risk_level":

        risk_level,

        "ai_explanation":

        explanations,

        "alert_created":

        alert_created

    }), 201

# ==========================================
# GET LATEST CHECK-IN
# ==========================================

@app.route("/victim/<victim_id>/latest-checkin", methods=["GET"])
def get_latest_checkin(victim_id):


    latest_checkin = Checkin.query.filter_by(
        victim_id=victim_id
    ).order_by(
        Checkin.created_at.desc()
    ).first()


    # --------------------------------------
    # NO CHECK-IN FOUND
    # --------------------------------------

    if not latest_checkin:

        return jsonify({

            "message": "No check-in found",

            "checkin": None

        }), 200


    # --------------------------------------
    # RETURN LATEST CHECK-IN
    # --------------------------------------

    return jsonify({

        "victim_id": latest_checkin.victim_id,

        "mood": latest_checkin.mood,

        "safety": latest_checkin.safety,

        "fear_level": latest_checkin.fear_level,

        "ddi_score": latest_checkin.ddi_score,

        "risk_level": latest_checkin.risk_level,

        "text_response": latest_checkin.text_response,

        "created_at": latest_checkin.created_at.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    }), 200

# ==========================================
# GET ALL CHECK-INS FOR A VICTIM
# ==========================================

@app.route("/victim/<victim_id>/checkins", methods=["GET"])
def get_victim_checkins(victim_id):

    checkins = Checkin.query.filter_by(
        victim_id=victim_id
    ).order_by(
        Checkin.created_at.asc()
    ).all()


    # --------------------------------------
    # RETURN ALL CHECK-INS
    # --------------------------------------

    checkin_list = []


    for checkin in checkins:

        checkin_list.append({

            "id": checkin.id,

            "victim_id": checkin.victim_id,

            "mood": checkin.mood,

            "safety": checkin.safety,

            "fear_level": checkin.fear_level,

            "ddi_score": checkin.ddi_score,

            "risk_level": checkin.risk_level,

            "created_at": checkin.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        })


    return jsonify({

        "victim_id": victim_id,

        "total_checkins": len(checkin_list),

        "checkins": checkin_list

    }), 200

# ==========================================
# CREATE EMERGENCY HELP ALERT
# ==========================================

@app.route("/victim/<victim_id>/help", methods=["POST"])
def request_help(victim_id):

    try:

        # --------------------------------------
        # Find victim's latest check-in
        # --------------------------------------

        latest_checkin = Checkin.query.filter_by(
            victim_id=victim_id
        ).order_by(
            Checkin.created_at.desc()
        ).first()


        # --------------------------------------
        # Create alert
        # --------------------------------------

        new_alert = Alert(

            victim_id=victim_id,

            checkin_id=(
                latest_checkin.id
                if latest_checkin
                else None
            ),

            risk_level=(
                latest_checkin.risk_level
                if latest_checkin
                else "High"
            ),

            status="Pending"

        )


        db.session.add(new_alert)

        db.session.commit()


        return jsonify({

            "message":
                "Help request sent successfully.",

            "alert_id":
                new_alert.id,

            "victim_id":
                victim_id,

            "status":
                new_alert.status,

            "risk_level":
                new_alert.risk_level

        }), 201


    except Exception as e:

        db.session.rollback()

        print(
            "Help request error:",
            e
        )

        return jsonify({

            "error":
                "Unable to create help request."

        }), 500
    
# ==========================================
# COUNSELLOR - GET VICTIM DETAILS
# ==========================================



@app.route("/counsellor/victim/<victim_id>", methods=["GET"])
def get_counsellor_victim(victim_id):

    try:

        # --------------------------------------
        # Get all check-ins for this victim
        # --------------------------------------

        checkins = Checkin.query.filter_by(
            victim_id=victim_id
        ).order_by(
            Checkin.created_at.asc()
        ).all()


        # --------------------------------------
        # Check whether victim has any data
        # --------------------------------------

        if not checkins:

            return jsonify({

                "error":
                    "No check-in data found for this victim."

            }), 404


        checkin_list = []


        # --------------------------------------
        # Distress keywords
        # --------------------------------------

        distress_keywords = [

            "scared",
            "afraid",
            "unsafe",
            "help",
            "danger",
            "fear",
            "threat",
            "worried",
            "anxious",
            "alone"

        ]


        # --------------------------------------
        # Process every check-in
        # --------------------------------------

        for checkin in checkins:

            explanations = []


            # ------------------------------
            # Mood analysis
            # ------------------------------

            if checkin.mood == "Scared":

                explanations.append(
                    "Fear-related emotional indicators detected."
                )

            elif checkin.mood in [
                "Sad",
                "Stressed"
            ]:

                explanations.append(
                    "Negative emotional indicators detected."
                )


            # ------------------------------
            # Safety analysis
            # ------------------------------

            if checkin.safety == "No":

                explanations.append(
                    "Victim reported feeling unsafe."
                )


            # ------------------------------
            # Fear analysis
            # ------------------------------

            if checkin.fear_level >= 7:

                explanations.append(
                    "High fear or anxiety level reported."
                )


            # ------------------------------
            # Text analysis
            # ------------------------------

            text = checkin.text_response or ""

            text_lower = text.lower()


            detected_keywords = []


            for keyword in distress_keywords:

                if keyword in text_lower:

                    detected_keywords.append(
                        keyword
                    )


            if detected_keywords:

                explanations.append(

                    "Distress-related language detected: "
                    +
                    ", ".join(
                        detected_keywords
                    )

                )


            # ------------------------------
            # Add check-in
            # ------------------------------

            checkin_list.append({

                "id":
                    checkin.id,

                "victim_id":
                    checkin.victim_id,

                "mood":
                    checkin.mood,

                "safety":
                    checkin.safety,

                "fear_level":
                    checkin.fear_level,

                "text_response":
                    text,

                "ddi_score":
                    checkin.ddi_score,

                "risk_level":
                    checkin.risk_level,

                "ai_explanation":
                    explanations,

                "created_at":

                    (
                        checkin.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        if checkin.created_at

                        else ""

                    )

            })


        # --------------------------------------
        # Return victim information
        # --------------------------------------

        return jsonify({

            "victim_id":
                victim_id,

            "total_checkins":
                len(checkin_list),

            "checkins":
                checkin_list

        }), 200


    except Exception as e:

        print(
            "COUNSELLOR VICTIM ERROR:",
            e
        )


        return jsonify({

            "error":
                "Unable to load victim details.",

            "details":
                str(e)

        }), 500
    

# ==========================================
# COUNSELLOR - GET ALL ALERTS
# ==========================================

@app.route("/counsellor/alerts", methods=["GET"])
def get_counsellor_alerts():

    try:

        alerts = Alert.query.order_by(
            Alert.created_at.desc()
        ).all()

        alert_list = []

        for alert in alerts:

            # Find the check-in associated with this alert
            checkin = Checkin.query.filter_by(
                id=alert.checkin_id
            ).first()

            alert_list.append({

                "alert_id": alert.id,

                "victim_id": alert.victim_id,

                "checkin_id": alert.checkin_id,

                "risk_level": alert.risk_level,

                "status": alert.status,

                "follow_up_date":

    (
        alert.follow_up_date.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        if alert.follow_up_date

        else None

    ),

                "mood": checkin.mood if checkin else "N/A",

                "safety": checkin.safety if checkin else "N/A",

                "fear_level": checkin.fear_level if checkin else 0,

                "ddi_score": checkin.ddi_score if checkin else 0,

                "created_at": alert.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            })

        return jsonify({

            "total_alerts": len(alert_list),

            "alerts": alert_list

        }), 200

    except Exception as e:

        print(
            "Counsellor alerts error:",
            e
        )

        return jsonify({

            "error":
                "Unable to load counsellor alerts."

        }), 500
    

# ==========================================
# COUNSELLOR - UPDATE ALERT STATUS
# ==========================================

@app.route(
    "/counsellor/alert/<int:alert_id>/status",
    methods=["PUT"]
)
def update_alert_status(alert_id):

    try:

        data = request.get_json()

        new_status = data.get("status")

        follow_up_date = data.get(
            "follow_up_date"
        )


        # --------------------------------------
        # VALID STATUSES
        # --------------------------------------

        allowed_statuses = [

            "Pending",
            "Contacted",
            "Counselling",
            "Follow-up",
            "Resolved"

        ]


        if new_status not in allowed_statuses:

            return jsonify({

                "error":
                    "Invalid alert status."

            }), 400


        # --------------------------------------
        # FIND ALERT
        # --------------------------------------

        alert = Alert.query.get(alert_id)


        if not alert:

            return jsonify({

                "error":
                    "Alert not found."

            }), 404


        # --------------------------------------
        # UPDATE STATUS
        # --------------------------------------

        alert.status = new_status


        # --------------------------------------
        # HANDLE FOLLOW-UP DATE
        # --------------------------------------

        if new_status == "Follow-up":

            if not follow_up_date:

                return jsonify({

                    "error":
                        "Follow-up date is required."

                }), 400


            try:

                alert.follow_up_date = datetime.strptime(

                    follow_up_date,

                    "%Y-%m-%dT%H:%M"

                )

            except ValueError:

                return jsonify({

                    "error":
                        "Invalid follow-up date format."

                }), 400


        else:

            # Clear follow-up date when the
            # alert moves to another status

            alert.follow_up_date = None


        # --------------------------------------
        # SAVE TO DATABASE
        # --------------------------------------

        db.session.commit()


        # --------------------------------------
        # RESPONSE
        # --------------------------------------

        return jsonify({

            "message":
                "Alert status updated successfully.",

            "alert_id":
                alert.id,

            "victim_id":
                alert.victim_id,

            "status":
                alert.status,

            "follow_up_date":

                (
                    alert.follow_up_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if alert.follow_up_date

                    else None

                )

        }), 200


    except Exception as e:

        db.session.rollback()

        print(
            "Status update error:",
            e
        )

        return jsonify({

            "error":
                "Unable to update alert status."

        }), 500
    

# ==========================================
# COUNSELLOR - GET SCHEDULED FOLLOW-UPS
# ==========================================

@app.route(
    "/counsellor/followups",
    methods=["GET"]
)
def get_followups():

    try:

        # --------------------------------------
        # GET ALL ALERTS WITH FOLLOW-UP STATUS
        # --------------------------------------

        followup_alerts = Alert.query.filter_by(
            status="Follow-up"
        ).order_by(
            Alert.follow_up_date.asc()
        ).all()


        followup_list = []


        # --------------------------------------
        # PREPARE FOLLOW-UP DATA
        # --------------------------------------

        for alert in followup_alerts:

            followup_list.append({

                "alert_id":
                    alert.id,

                "victim_id":
                    alert.victim_id,

                "risk_level":
                    alert.risk_level,

                "status":
                    alert.status,

                "follow_up_date":

                    alert.follow_up_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if alert.follow_up_date

                    else None

            })


        # --------------------------------------
        # RETURN FOLLOW-UPS
        # --------------------------------------

        return jsonify({

            "total_followups":
                len(followup_list),

            "followups":
                followup_list

        }), 200


    except Exception as e:

        print(
            "Follow-up loading error:",
            e
        )


        return jsonify({

            "error":
                "Unable to load follow-ups.",

            "details":
                str(e)

        }), 500
    

# ==========================================
# COUNSELLOR - COMPLETE FOLLOW-UP
# ==========================================

@app.route(
    "/counsellor/alert/<int:alert_id>/follow-up/complete",
    methods=["PUT"]
)
def complete_follow_up(alert_id):

    try:

        # --------------------------------------
        # FIND ALERT
        # --------------------------------------

        alert = Alert.query.get(alert_id)

        if not alert:

            return jsonify({

                "error":
                    "Alert not found."

            }), 404


        # --------------------------------------
        # CHECK CURRENT STATUS
        # --------------------------------------

        if alert.status != "Follow-up":

            return jsonify({

                "error":
                    "This alert is not currently scheduled for follow-up."

            }), 400


        # --------------------------------------
        # MARK FOLLOW-UP AS COMPLETED
        # --------------------------------------

        alert.status = "Resolved"


        # Keep follow_up_date as a historical record

        db.session.commit()


        # --------------------------------------
        # RETURN SUCCESS
        # --------------------------------------

        return jsonify({

            "message":
                "Follow-up completed successfully.",

            "alert_id":
                alert.id,

            "victim_id":
                alert.victim_id,

            "status":
                alert.status,

            "follow_up_date":

                (
                    alert.follow_up_date.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    if alert.follow_up_date

                    else None
                )

        }), 200


    except Exception as e:

        db.session.rollback()

        print(
            "Follow-up completion error:",
            e
        )

        return jsonify({

            "error":
                "Unable to complete follow-up."

        }), 500


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

with app.app_context():

    db.create_all()


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    app.run(

        debug=True,

        port=5000

    )