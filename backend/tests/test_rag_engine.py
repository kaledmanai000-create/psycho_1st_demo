"""Tests for the RAG Engine component."""

import pytest
from app.ai_engine.rag_engine import RAGEngine


class TestRAGEngine:
    @pytest.fixture(scope="class")
    def engine(self):
        return RAGEngine()

    def test_index_built(self, engine):
        assert engine.index is not None
        assert engine.vectorizer is not None
        assert len(engine.patterns) > 0

    def test_search_returns_dict(self, engine):
        result = engine.search("Your account has been compromised. Click here to verify.")
        assert isinstance(result, dict)
        assert "matches" in result
        assert "max_similarity" in result
        assert "explanations" in result
        assert "rag_score" in result

    def test_search_phishing_finds_matches(self, engine):
        result = engine.search(
            "Your account has been compromised. Click here to verify your identity immediately."
        )
        assert result["max_similarity"] > 0.0
        assert len(result["matches"]) > 0

    def test_search_safe_content_low_similarity(self, engine):
        result = engine.search(
            "The restaurant received positive reviews for its new seasonal menu."
        )
        # Safe content should have lower similarity to threat patterns
        assert result["max_similarity"] < 0.8

    def test_search_top_k(self, engine):
        result = engine.search("Verify your bank account now", top_k=2)
        assert len(result["matches"]) <= 2

    def test_patterns_have_required_fields(self, engine):
        for pattern in engine.patterns:
            assert "text" in pattern
            assert "category" in pattern
