"""Main Analysis Pipeline - orchestrates all AI components."""

from app.ai_engine.preprocessor import Preprocessor
from app.ai_engine.feature_extractor import FeatureExtractor
from app.ai_engine.rule_engine import RuleEngine
from app.ai_engine.ml_classifier import MLClassifier
from app.ai_engine.rag_engine import RAGEngine
from app.explainability import ExplainabilityLayer


class AnalysisPipeline:
    """
    Orchestrates the full analysis pipeline:
    Preprocess -> Feature Extraction -> Rule Engine -> ML Classifier -> RAG -> Combine
    """

    def __init__(self):
        self.preprocessor = Preprocessor()
        self.feature_extractor = FeatureExtractor()
        self.rule_engine = RuleEngine()
        self.ml_classifier = MLClassifier()
        self.rag_engine = RAGEngine()
        self.explainability = ExplainabilityLayer()

    def analyze(self, text: str) -> dict:
        """
        Run the full analysis pipeline on input text.
        Returns: {risk_score, threat_type, explanation, confidence}
        """
        # Step 1: Preprocess
        preprocessed = self.preprocessor.preprocess(text)

        # Step 2: Feature Extraction
        features = self.feature_extractor.extract(preprocessed)

        # Step 3: Rule-based Analysis
        rule_result = self.rule_engine.analyze(features, preprocessed)

        # Step 4: ML Classification
        ml_result = self.ml_classifier.predict(preprocessed["cleaned_text"])

        # Step 5: RAG - Compare with known patterns
        rag_result = self.rag_engine.search(preprocessed["cleaned_text"])

        # Step 6: Combine all results
        combined = self._combine_results(rule_result, ml_result, rag_result, features)

        # Step 7: Generate final explanations
        explanation = self.explainability.generate(
            rule_explanations=rule_result["explanations"],
            rag_explanations=rag_result["explanations"],
            ml_label=ml_result["label"],
            ml_confidence=ml_result["confidence"],
            features=features,
        )

        return {
            "risk_score": combined["risk_score"],
            "threat_type": combined["threat_type"],
            "explanation": explanation,
            "confidence": combined["confidence"],
        }

    def _combine_results(
        self, rule_result: dict, ml_result: dict, rag_result: dict, features: dict
    ) -> dict:
        """
        Combine scores from all components using weighted average.
        Weights: Rule engine (40%), ML classifier (30%), RAG (30%)
        """
        # Get individual scores
        rule_score = rule_result.get("rule_score", 0)
        rag_score = rag_result.get("rag_score", 0)

        # Convert ML confidence to a risk score
        ml_label = ml_result["label"]
        ml_confidence = ml_result["confidence"]
        ml_risk = 0
        if ml_label != "safe":
            ml_risk = ml_confidence * 100
        else:
            ml_risk = (1 - ml_confidence) * 30  # Low risk if predicted safe

        # Weighted combination
        risk_score = int(
            rule_score * 0.40
            + ml_risk * 0.30
            + rag_score * 0.30
        )
        risk_score = max(0, min(100, risk_score))

        # Determine threat type from consensus
        threat_type = self._determine_threat_type(rule_result, ml_result, features)

        # Confidence is average of individual confidences
        rule_confidence = min(rule_score / 100, 1.0) if rule_score > 0 else 0.3
        rag_confidence = min(rag_score / 100, 1.0) if rag_score > 0 else 0.2
        confidence = round(
            (rule_confidence * 0.4 + ml_confidence * 0.3 + rag_confidence * 0.3), 2
        )

        return {
            "risk_score": risk_score,
            "threat_type": threat_type,
            "confidence": max(0.0, min(1.0, confidence)),
        }

    def _determine_threat_type(self, rule_result: dict, ml_result: dict, features: dict) -> str:
        """Determine the primary threat type based on all signals."""
        scores = {
            "phishing": features.get("phishing_score", 0),
            "manipulation": features.get("manipulation_score", 0),
            "disinformation": features.get("disinformation_score", 0),
        }

        # Boost the ML prediction's category
        ml_label = ml_result["label"]
        if ml_label in scores:
            scores[ml_label] += ml_result["confidence"] * 30

        # Get highest scoring category
        threat_type = max(scores, key=scores.get)
        max_score = scores[threat_type]

        if max_score < 10:
            return "safe"

        return threat_type
