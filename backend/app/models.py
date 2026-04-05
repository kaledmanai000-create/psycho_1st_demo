"""Pydantic models for request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=50000, description="Text content to analyze")


class AnalyzeResponse(BaseModel):
    risk_score: int = Field(..., ge=0, le=100, description="Risk score from 0 (safe) to 100 (critical)")
    threat_type: str = Field(..., description="Type of threat detected")
    explanation: list[str] = Field(default_factory=list, description="Human-readable explanations")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level of the analysis")
    details: Optional[dict] = Field(default=None, description="Optional subsystem and fusion debug details")


class BatchAnalyzeRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=50, description="List of texts to analyze (max 50)")


class BatchAnalyzeResponse(BaseModel):
    results: list[AnalyzeResponse] = Field(..., description="Analysis results for each text")
    total: int = Field(..., description="Total number of texts analyzed")


class LogRequest(BaseModel):
    input_text: str = Field(..., description="Original text that was analyzed")
    ai_decision: dict = Field(..., description="The AI analysis result")
    user_decision: str = Field(..., description="User's decision: ignore, investigate, or mark_as_threat")


class LogResponse(BaseModel):
    status: str = Field(default="logged", description="Status of the log operation")
    log_id: int = Field(..., description="ID of the created log entry")
