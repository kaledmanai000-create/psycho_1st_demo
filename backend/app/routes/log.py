"""POST /log endpoint - stores user decisions for transparency."""

from fastapi import APIRouter, HTTPException
from app.models import LogRequest, LogResponse
from app.database import log_decision, get_logs

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
