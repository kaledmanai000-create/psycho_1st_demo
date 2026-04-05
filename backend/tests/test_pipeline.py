"""Tests for the full analysis pipeline."""

import pytest
from app.ai_engine.pipeline import AnalysisPipeline


@pytest.fixture(scope="module")
def pipeline():
    return AnalysisPipeline()


class TestPipeline:
    def test_safe_content(self, pipeline):
        result = pipeline.analyze(
            "The quarterly earnings report showed stable growth. Revenue increased by 5% compared to last year."
        )
        assert "risk_score" in result
        assert "threat_type" in result
        assert "explanation" in result
        assert "confidence" in result
        assert result["risk_score"] >= 0
        assert result["risk_score"] <= 100
        assert result["confidence"] >= 0.0
        assert result["confidence"] <= 1.0

    def test_phishing_content(self, pipeline):
        result = pipeline.analyze(
            "URGENT: Your bank account has been compromised! Click here immediately to verify your identity "
            "and enter your password to restore access. Failure to act within 24 hours will result in permanent deletion."
        )
        assert result["risk_score"] > 20
        assert result["threat_type"] in ("phishing", "manipulation", "disinformation")

    def test_disinformation_content(self, pipeline):
        result = pipeline.analyze(
            "They don't want you to know the truth! The government is secretly controlling the weather. "
            "Mainstream media is hiding this shocking discovery. Share this before they delete it!"
        )
        assert result["risk_score"] > 10
        assert result["threat_type"] in ("disinformation", "manipulation", "phishing")

    def test_returns_explanations(self, pipeline):
        result = pipeline.analyze(
            "Your PayPal account needs immediate verification. Enter your credit card details now or lose access forever."
        )
        assert isinstance(result["explanation"], list)

    def test_short_text(self, pipeline):
        result = pipeline.analyze("Hello world, this is a test of the system.")
        assert result["risk_score"] >= 0
        assert result["threat_type"] is not None
