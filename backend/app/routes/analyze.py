"""Analysis endpoints - single and batch text analysis for threats."""

from fastapi import APIRouter, Request, HTTPException
from app.models import AnalyzeRequest, AnalyzeResponse, BatchAnalyzeRequest, BatchAnalyzeResponse
from app.security import sanitize_input, check_prompt_injection

router = APIRouter()


@router.post("", response_model=AnalyzeResponse)
async def analyze_content(request: Request, body: AnalyzeRequest):
    """
    Analyze text content for phishing, manipulation, and disinformation.
    Returns a risk score, threat type, and human-readable explanations.
    No automatic actions are taken - only suggestions for the human user.
    """
    text = sanitize_input(body.text)

    if not text:
        raise HTTPException(status_code=400, detail="Text content is empty after sanitization")

    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Text content is too short for meaningful analysis")

    if check_prompt_injection(text):
        raise HTTPException(
            status_code=400,
            detail="Input contains potentially malicious patterns and cannot be processed"
        )

    pipeline = request.app.state.pipeline
    result = pipeline.analyze(text)

    return AnalyzeResponse(
        risk_score=result["risk_score"],
        threat_type=result["threat_type"],
        explanation=result["explanation"],
        confidence=result["confidence"],
        details=result.get("details"),
    )


@router.post("/batch", response_model=BatchAnalyzeResponse)
async def analyze_batch(request: Request, body: BatchAnalyzeRequest):
    """
    Analyze multiple texts in a single request (max 50).
    Returns analysis results for each text.
    """
    pipeline = request.app.state.pipeline
    results = []

    for text in body.texts:
        cleaned = sanitize_input(text)
        if not cleaned or len(cleaned) < 10:
            results.append(AnalyzeResponse(
                risk_score=0, threat_type="safe",
                explanation=["Text too short for analysis"], confidence=0.0
            ))
            continue

        if check_prompt_injection(cleaned):
            results.append(AnalyzeResponse(
                risk_score=0, threat_type="blocked",
                explanation=["Blocked: potentially malicious patterns detected"], confidence=1.0
            ))
            continue

        result = pipeline.analyze(cleaned)
        results.append(AnalyzeResponse(
            risk_score=result["risk_score"],
            threat_type=result["threat_type"],
            explanation=result["explanation"],
            confidence=result["confidence"],
        ))

    return BatchAnalyzeResponse(results=results, total=len(results))
