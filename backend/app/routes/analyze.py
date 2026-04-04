"""POST /analyze endpoint - analyzes text content for threats."""

from fastapi import APIRouter, Request, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse
from app.security import sanitize_input, check_prompt_injection

router = APIRouter()


@router.post("", response_model=AnalyzeResponse)
async def analyze_content(request: Request, body: AnalyzeRequest):
    """
    Analyze text content for phishing, manipulation, and disinformation.
    Returns a risk score, threat type, and human-readable explanations.
    No automatic actions are taken - only suggestions for the human user.
    """
    # Sanitize input
    text = sanitize_input(body.text)

    if not text:
        raise HTTPException(status_code=400, detail="Text content is empty after sanitization")

    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text content is too short for meaningful analysis")

    # Check for prompt injection
    if check_prompt_injection(text):
        raise HTTPException(
            status_code=400,
            detail="Input contains potentially malicious patterns and cannot be processed"
        )

    # Run analysis pipeline
    pipeline = request.app.state.pipeline
    result = pipeline.analyze(text)

    return AnalyzeResponse(
        risk_score=result["risk_score"],
        threat_type=result["threat_type"],
        explanation=result["explanation"],
        confidence=result["confidence"],
    )
