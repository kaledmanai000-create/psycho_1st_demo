"""Tests for the ML Classifier component."""

import pytest
import os
import tempfile
from app.ai_engine.ml_classifier import MLClassifier, LABEL_MAP, REVERSE_LABEL_MAP


class TestMLClassifier:
    @pytest.fixture(scope="class")
    def classifier(self):
        return MLClassifier()

    def test_model_loads(self, classifier):
        assert classifier.model is not None

    def test_predict_returns_dict(self, classifier):
        result = classifier.predict("Hello this is a normal text about everyday life")
        assert isinstance(result, dict)
        assert "label" in result
        assert "confidence" in result
        assert "probabilities" in result

    def test_predict_safe_content(self, classifier):
        result = classifier.predict(
            "The local community center announced new programs for youth and families."
        )
        assert result["label"] in REVERSE_LABEL_MAP.values()
        assert 0.0 <= result["confidence"] <= 1.0

    def test_predict_phishing_content(self, classifier):
        result = classifier.predict(
            "URGENT: Your account has been suspended. Click here to enter your password and verify now."
        )
        assert result["label"] in REVERSE_LABEL_MAP.values()

    def test_probabilities_sum_to_one(self, classifier):
        result = classifier.predict("Some test content for probability check")
        total = sum(result["probabilities"].values())
        assert abs(total - 1.0) < 0.01

    def test_label_maps(self):
        assert len(LABEL_MAP) == 4
        assert "safe" in LABEL_MAP
        assert "phishing" in LABEL_MAP
        assert "manipulation" in LABEL_MAP
        assert "disinformation" in LABEL_MAP
        for k, v in LABEL_MAP.items():
            assert REVERSE_LABEL_MAP[v] == k
