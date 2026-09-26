"""PAWS global audit helpers.

This module is deliberately compatible with the existing PAWS audit_logs table:
    log_id, user_id, action_role, action, entity_type, entity_id,
    victim_id, case_id, details, ip_address, created_at

It also exposes the legacy helper names used by the Officer/Auth code:
    log_audit
    insert_audit_log
    ensure_audit_logs_table
    classify_request
    request_audit_context
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from database.db import get_db_connection


EXPECTED_COLUMNS = {
    "log_id",
    "user_id",
    "action_role",
    "action",
    "entity_type",
    "entity_id",
    "victim_id",
    "case_id",
    "details",
    "ip_address",
    "created_at",
}


COMPATIBLE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    action_role VARCHAR(30) NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(80) NULL,
    entity_id VARCHAR(100) NULL,
    victim_id INT NULL,
    case_id INT NULL,
    details JSON NULL,
    ip_address VARCHAR(64) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_user_created (user_id, created_at),
    INDEX idx_audit_action (action),
    INDEX idx_audit_entity (entity_type, entity_id),
    INDEX idx_audit_created (created_at)
) ENGINE=InnoDB;
"""


def _get_columns(connection) -> set[str]:
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW COLUMNS FROM audit_logs")
        return {row[0] for row in cursor.fetchall()}
    finally:
        cursor.close()


def ensure_audit_logs_table(connection=None) -> bool:
    """Ensure an audit_logs table exists without replacing the user's schema."""
    own_connection = connection is None
    conn = connection or get_db_connection()
    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES LIKE 'audit_logs'")
        exists = cursor.fetchone() is not None
        if not exists:
            cursor.execute(COMPATIBLE_TABLE_SQL)
            conn.commit()
            return True
        return True
    except Exception as error:
        print("AUDIT TABLE SETUP WARNING:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        if own_connection and conn and conn.is_connected():
            conn.close()


def _normalise_details(details: Any, description: str, status: str) -> Dict[str, Any]:
    """Keep structured details JSON-safe while preserving the human-readable summary."""
    if isinstance(details, dict):
        result = dict(details)
    elif details is None:
        result = {}
    else:
        result = {"value": str(details)}

    result.setdefault("description", description or "PAWS action recorded.")
    result.setdefault("status", status or "SUCCESS")
    return result


def insert_audit_log(
    connection=None,
    user_id=None,
    action_role=None,
    action="SYSTEM",
    entity_type=None,
    entity_id=None,
    victim_id=None,
    case_id=None,
    description="",
    status="SUCCESS",
    details=None,
    ip_address=None,
    # backwards compatibility with older Officer patch
    officer_id=None,
    **kwargs,
) -> bool:
    """Insert an audit event using the live audit_logs schema.

    The existing PAWS database uses user_id/action_role/details rather than
    officer_id/status/description columns. Status and description are retained
    inside the JSON details field so no schema migration is required.
    """
    own_connection = connection is None
    conn = connection or get_db_connection()
    cursor = None

    # Accept both the current role-aware API and the older officer_id API.
    if user_id is None:
        user_id = officer_id
    if action_role is None:
        action_role = kwargs.get("role") or ("OFFICER" if officer_id is not None else "SYSTEM")

    try:
        ensure_audit_logs_table(conn)
        columns = _get_columns(conn)

        event_details = _normalise_details(details, description, status)

        field_values = {
            "user_id": user_id,
            "action_role": action_role,
            "action": action,
            "entity_type": entity_type,
            "entity_id": str(entity_id) if entity_id is not None else None,
            "victim_id": victim_id,
            "case_id": case_id,
            "details": json.dumps(event_details, ensure_ascii=False, default=str),
            "ip_address": ip_address,
        }

        usable = [
            name for name in (
                "user_id",
                "action_role",
                "action",
                "entity_type",
                "entity_id",
                "victim_id",
                "case_id",
                "details",
                "ip_address",
            )
            if name in columns
        ]

        if "action" not in usable:
            raise RuntimeError("audit_logs table has no action column")

        placeholders = ", ".join(["%s"] * len(usable))
        query = f"INSERT INTO audit_logs ({', '.join(usable)}) VALUES ({placeholders})"
        cursor = conn.cursor()
        cursor.execute(query, [field_values[name] for name in usable])
        conn.commit()
        return True
    except Exception as error:
        try:
            conn.rollback()
        except Exception:
            pass
        # Audit must never break a normal PAWS workflow.
        print("AUDIT LOG WARNING:", error)
        return False
    finally:
        if cursor:
            cursor.close()
        if own_connection and conn and conn.is_connected():
            conn.close()


def log_audit(*args, **kwargs) -> bool:
    """Public audit logger used by all PAWS roles."""
    return insert_audit_log(*args, **kwargs)


# =========================================================
# GLOBAL AUTHENTICATED ACTION AUDIT HELPERS
# =========================================================


def classify_request(path: str, method: str) -> Optional[Dict[str, Any]]:
    """Map meaningful API activity to stable audit actions.

    Navigation and audit endpoints are intentionally excluded so opening pages
    does not flood the history.
    """
    p = (path or "").rstrip("/") or "/"
    m = (method or "GET").upper()

    if p in {
        "/api/officer/audit-logs",
        "/api/auth/login",
        "/api/auth/logout",
        "/api/auth/me",
    }:
        return None

    # Victim actions
    if p == "/api/victims/help" and m == "POST":
        return {
            "action": "SOS_REQUESTED",
            "entity_type": "ALERT",
            "entity_id": None,
            "description": "Victim requested immediate support (SOS).",
        }

    # Role-specific SOS review
    match = re.fullmatch(r"/api/(officer|counsellor)/alerts/(\d+)/review", p)
    if match and m == "PUT":
        role_name = match.group(1).title()
        return {
            "action": "SOS_REVIEWED",
            "entity_type": "ALERT",
            "entity_id": match.group(2),
            "description": f"{role_name} reviewed SOS alert {match.group(2)}.",
        }

    if p == "/api/counsellor/interventions" and m == "POST":
        return {
            "action": "INTERVENTION_RECORDED",
            "entity_type": "INTERVENTION",
            "entity_id": None,
            "description": "Counsellor recorded a support intervention.",
        }

    match = re.fullmatch(r"/api/counsellor/followups/(\d+)/complete", p)
    if match and m == "PUT":
        return {
            "action": "FOLLOWUP_COMPLETED",
            "entity_type": "FOLLOWUP",
            "entity_id": match.group(1),
            "description": f"Counsellor completed follow-up {match.group(1)}.",
        }

    match = re.fullmatch(r"/api/cases/(\d+)/stage", p)
    if match and m == "PUT":
        return {
            "action": "CASE_STAGE_CHANGED",
            "entity_type": "CASE",
            "entity_id": match.group(1),
            "description": f"Case {match.group(1)} stage was updated.",
        }

    return None


def request_audit_context(request_obj, response_obj, metadata):
    """Enrich an authenticated action with response/request context."""
    action = dict(metadata)
    try:
        payload = response_obj.get_json(silent=True) or {}
        request_body = request_obj.get_json(silent=True) or {}
    except Exception:
        payload = {}
        request_body = {}

    if action.get("action") == "SOS_REQUESTED":
        action["entity_id"] = payload.get("alert_id") or action.get("entity_id")
        action["victim_id"] = payload.get("victim_id") or request_body.get("victim_id")

    if action.get("action") == "INTERVENTION_RECORDED":
        action["entity_id"] = payload.get("intervention_id") or action.get("entity_id")
        if request_body.get("victim_id") is not None:
            action["victim_id"] = request_body.get("victim_id")
        if request_body.get("alert_id") is not None:
            action["details_alert_id"] = request_body.get("alert_id")

    status_code = getattr(response_obj, "status_code", 500)
    action["status"] = "SUCCESS" if status_code < 400 else "FAILED"
    action["response_status"] = status_code
    return action
