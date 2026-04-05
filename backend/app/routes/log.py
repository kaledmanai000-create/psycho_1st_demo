"""POST /log endpoint - stores user decisions for transparency."""

import csv
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models import LogRequest, LogResponse
from app.database import log_decision, get_logs, get_connection

router = APIRouter()


@router.post("", response_model=LogResponse)
async def log_user_decision(body: LogRequest):
    """
    Log the user's decision about an analysis result.
    This enforces human-in-the-loop: AI suggests, human decides, decision is recorded.
    """
    valid_decisions = {"ignore", "investigate", "mark_as_threat"}
    if body.user_decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision. Must be one of: {', '.join(valid_decisions)}"
        )

    ai_decision = body.ai_decision
    log_id = log_decision(
        input_text=body.input_text,
        risk_score=ai_decision.get("risk_score", 0),
        threat_type=ai_decision.get("threat_type", "unknown"),
        explanation=ai_decision.get("explanation", []),
        confidence=ai_decision.get("confidence", 0.0),
        user_decision=body.user_decision,
    )

    return LogResponse(status="logged", log_id=log_id)


@router.get("/history")
async def get_log_history(limit: int = 50):
    """Retrieve recent analysis logs for transparency dashboard."""
    return {"logs": get_logs(limit=min(limit, 200))}


@router.get("/export")
async def export_logs_csv():
    """Export all analysis logs as a downloadable CSV file."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "id",
        "input_text",
        "risk_score",
        "threat_type",
        "explanation",
        "confidence",
        "user_decision",
        "timestamp",
    ])

    for row in rows:
        writer.writerow([
            row["id"],
            row["input_text"][:500],
            row["risk_score"],
            row["threat_type"],
            row["explanation"],
            row["confidence"],
            row["user_decision"],
            row["timestamp"],
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=cognitive_shield_logs.csv"},
    )
