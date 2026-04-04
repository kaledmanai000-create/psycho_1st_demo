"""SQLite database layer for logging analysis decisions."""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cognitive_shield.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
