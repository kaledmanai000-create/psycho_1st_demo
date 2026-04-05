"""SQLite database layer for logging analysis decisions."""

import sqlite3
import json
import os
from datetime import datetime

from app.config import get_settings


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    db_path = get_settings().db_path
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            input_text TEXT NOT NULL,
            risk_score INTEGER NOT NULL,
            threat_type TEXT NOT NULL,
            explanation TEXT NOT NULL,
            confidence REAL NOT NULL,
            user_decision TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            method TEXT NOT NULL,
            path TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            client_ip TEXT,
            duration_ms REAL,
            request_body TEXT,
            response_summary TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_decision(
    input_text: str,
    risk_score: int,
    threat_type: str,
    explanation: list[str],
    confidence: float,
    user_decision: str,
) -> int:
    """Log an analysis decision to the database. Returns the log ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO analysis_logs (input_text, risk_score, threat_type, explanation, confidence, user_decision, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            input_text[:5000],  # Truncate for storage safety
            risk_score,
            threat_type,
            json.dumps(explanation),
            confidence,
            user_decision,
            datetime.utcnow().isoformat(),
        ),
    )
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_logs(limit: int = 100) -> list[dict]:
    """Retrieve recent analysis logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM analysis_logs ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "input_text": row["input_text"][:200] + "..." if len(row["input_text"]) > 200 else row["input_text"],
            "risk_score": row["risk_score"],
            "threat_type": row["threat_type"],
            "explanation": json.loads(row["explanation"]),
            "confidence": row["confidence"],
            "user_decision": row["user_decision"],
            "timestamp": row["timestamp"],
        }
        for row in rows
    ]


def log_request(
    method: str,
    path: str,
    status_code: int,
    client_ip: str,
    duration_ms: float,
    request_body: str = "",
    response_summary: str = "",
) -> int:
    """Log an HTTP request to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO request_logs (method, path, status_code, client_ip, duration_ms, request_body, response_summary, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            method,
            path[:500],
            status_code,
            client_ip,
            round(duration_ms, 2),
            request_body[:2000],
            response_summary[:1000],
            datetime.utcnow().isoformat(),
        ),
    )
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def get_request_logs(limit: int = 200) -> list[dict]:
    """Retrieve recent request logs."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM request_logs ORDER BY id DESC LIMIT ?",
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "method": row["method"],
            "path": row["path"],
            "status_code": row["status_code"],
            "client_ip": row["client_ip"],
            "duration_ms": row["duration_ms"],
            "request_body": row["request_body"],
            "response_summary": row["response_summary"],
            "timestamp": row["timestamp"],
        }
        for row in rows
    ]
