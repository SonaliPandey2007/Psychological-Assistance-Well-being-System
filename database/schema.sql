CREATE DATABASE IF NOT EXISTS paws_db;

USE paws_db;

-- 1. USERS
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('OFFICER', 'COUNSELLOR', 'VICTIM') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. VICTIMS
CREATE TABLE victims (
    victim_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    victim_code VARCHAR(50) UNIQUE NOT NULL,
    age INT,
    gender VARCHAR(20),
    preferred_language VARCHAR(30) DEFAULT 'Hindi',
    safety_status ENUM('SAFE', 'CONCERN', 'DANGER') DEFAULT 'SAFE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);

-- 3. CASES
CREATE TABLE cases (
    case_id INT AUTO_INCREMENT PRIMARY KEY,
    victim_id INT NOT NULL,
    case_number VARCHAR(100) UNIQUE NOT NULL,
    case_type VARCHAR(150),

    current_stage ENUM(
        'COMPLAINT',
        'INVESTIGATION',
        'TRIAL',
        'COMPENSATION',
        'REHABILITATION'
    ) DEFAULT 'COMPLAINT',

    assigned_officer INT,
    assigned_counsellor INT,

    case_status ENUM(
        'ACTIVE',
        'ON_HOLD',
        'CLOSED'
    ) DEFAULT 'ACTIVE',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (victim_id)
        REFERENCES victims(victim_id)
        ON DELETE CASCADE,

    FOREIGN KEY (assigned_officer)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    FOREIGN KEY (assigned_counsellor)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);

-- 4. CHECK-INS
CREATE TABLE check_ins (
    checkin_id INT AUTO_INCREMENT PRIMARY KEY,
    victim_id INT NOT NULL,
    case_id INT,

    mood_score INT,
    safety_score INT,
    stress_level INT,

    text_response TEXT,

    engagement_score DECIMAL(5,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (victim_id)
        REFERENCES victims(victim_id)
        ON DELETE CASCADE,

    FOREIGN KEY (case_id)
        REFERENCES cases(case_id)
        ON DELETE SET NULL
);

-- 5. AI DISTRESS SCORES
CREATE TABLE distress_scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    victim_id INT NOT NULL,
    checkin_id INT,

    distress_index DECIMAL(5,2),

    risk_level ENUM(
        'LOW',
        'MODERATE',
        'HIGH'
    ),

    fear_score DECIMAL(5,2),
    stress_score DECIMAL(5,2),
    negative_emotion_score DECIMAL(5,2),
    behaviour_score DECIMAL(5,2),

    explanation TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (victim_id)
        REFERENCES victims(victim_id)
        ON DELETE CASCADE,

    FOREIGN KEY (checkin_id)
        REFERENCES check_ins(checkin_id)
        ON DELETE SET NULL
);

-- 6. ALERTS
CREATE TABLE alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    victim_id INT NOT NULL,
    score_id INT,

    alert_type VARCHAR(100),

    severity ENUM(
        'LOW',
        'MODERATE',
        'HIGH'
    ),

    message TEXT,

    is_reviewed BOOLEAN DEFAULT FALSE,

    reviewed_by INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (victim_id)
        REFERENCES victims(victim_id)
        ON DELETE CASCADE,

    FOREIGN KEY (score_id)
        REFERENCES distress_scores(score_id)
        ON DELETE SET NULL,

    FOREIGN KEY (reviewed_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL
);