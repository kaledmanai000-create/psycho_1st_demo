import os
import sys

import pytest

# Ensure imports work when running from repository root.
BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.ai_engine.pipeline import AnalysisPipeline


@pytest.fixture(scope="module")
def pipeline() -> AnalysisPipeline:
    return AnalysisPipeline()


def test_phishing_example_detected(pipeline: AnalysisPipeline):
    text = "URGENT: Your bank account is suspended. Verify your password now at http://verify-account-secure-login.xyz"
    result = pipeline.analyze(text)
    assert result["threat_type"] == "phishing"
    assert result["risk_score"] >= 35
    assert result["details"]["triggered_rules"]


def test_manipulation_example_detected(pipeline: AnalysisPipeline):
    text = "If you are a real Tunisian, share this now. سكوتك خيانة ولازم الكل يعرف قبل ما يمسحوها"
    result = pipeline.analyze(text)
    assert result["threat_type"] in {"manipulation", "disinformation"}
    assert result["risk_score"] >= 45


def test_disinformation_example_detected(pipeline: AnalysisPipeline):
    text = "The media is hiding the truth about this miracle cure. Share before they delete it!"
    result = pipeline.analyze(text)
    assert result["threat_type"] in {"disinformation", "manipulation"}
    assert result["risk_score"] >= 40


def test_safe_example_low_risk(pipeline: AnalysisPipeline):
    text = "Team meeting moved to 3 PM tomorrow. Please bring the updated quarterly report."
    result = pipeline.analyze(text)
    assert result["threat_type"] == "safe"
    assert result["risk_score"] <= 35


def test_url_signals_for_ip_and_punycode(pipeline: AnalysisPipeline):
    text = "Confirm your login here: http://192.168.1.2/reset and http://xn--pple-43d.com/verify"
    preprocessed = pipeline.preprocessor.preprocess(text)
    features = pipeline.feature_extractor.extract(preprocessed)
    matched = " ".join(features["suspicious_urls"]["matched"])
    assert "ip_based_url" in matched
    assert "punycode_domain" in matched


def test_false_positive_prone_legitimate_message(pipeline: AnalysisPipeline):
    text = "Reminder: Your internet subscription expires next month. Renew through the official provider app only."
    result = pipeline.analyze(text)
    assert result["risk_score"] <= 45


def test_ambiguous_case_has_explainability_details(pipeline: AnalysisPipeline):
    text = "Act quickly, this is shocking and important, but verify from official sources before sharing."
    result = pipeline.analyze(text)
    details = result.get("details", {})
    assert "subsystem_scores" in details
    assert "fusion_reasoning" in details
    assert "ml_top_features" in details
    assert "retrieved_patterns" in details
