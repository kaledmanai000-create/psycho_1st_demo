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
            fusion_reasoning=combined["fusion_reasoning"],
        )

        return {
            "risk_score": combined["risk_score"],
            "threat_type": combined["threat_type"],
            "explanation": explanation,
            "confidence": combined["confidence"],
            "details": {
                "subsystem_scores": combined["subsystem_scores"],
                "fusion_reasoning": combined["fusion_reasoning"],
                "triggered_rules": rule_result.get("triggered_rules", []),
                "ml_probabilities": ml_result.get("probabilities", {}),
                "ml_top_features": ml_result.get("top_features", []),
                "retrieved_patterns": rag_result.get("matches", []),
                "model_version": ml_result.get("model_version", "unknown"),
            },
        }

    def _combine_results(
        self, rule_result: dict, ml_result: dict, rag_result: dict, features: dict
    ) -> dict:
        """Combine subsystems with confidence-aware per-class fusion and safe gating."""
        classes = ["phishing", "manipulation", "disinformation"]
        ml_probs = ml_result.get("probabilities", {})
        rule_scores = rule_result.get("scores", {})
        rag_scores = rag_result.get("category_scores", {})

        weights = {"rule": 0.35, "ml": 0.40, "rag": 0.25}
        fusion_reasoning = []
        ml_conf = float(ml_result.get("confidence", 0.0))

        if ml_result.get("label") != "safe" and ml_conf >= 0.80:
            weights = {"rule": 0.25, "ml": 0.55, "rag": 0.20}
            fusion_reasoning.append("High-confidence ML prediction increased ML weight")
        elif rule_result.get("rule_score", 0) >= 70:
            weights = {"rule": 0.50, "ml": 0.30, "rag": 0.20}
            fusion_reasoning.append("Strong rule-based evidence increased rule weight")

        fused_per_class = {}
        for c in classes:
            rule_component = float(rule_scores.get(c, 0.0))
            ml_component = float(ml_probs.get(c, 0.0)) * 100
            rag_component = float(rag_scores.get(c, 0.0)) * 100
            fused_per_class[c] = (
                rule_component * weights["rule"]
                + ml_component * weights["ml"]
                + rag_component * weights["rag"]
            )

        best_class = max(fused_per_class, key=fused_per_class.get)
        best_score = fused_per_class[best_class]
        safe_prob = float(ml_probs.get("safe", 0.0))

        if best_score < 30 and safe_prob >= 0.35 and rule_result.get("rule_score", 0) < 20:
            threat_type = "safe"
            fusion_reasoning.append("Low fused threat score with moderate safe probability triggered safe gating")
        else:
            threat_type = best_class

        non_safe_prob_mass = sum(float(ml_probs.get(c, 0.0)) for c in classes)
        risk_score = int(min(max((best_score * 0.8) + (non_safe_prob_mass * 20), 0), 100))

        confidence = round(
            min(max(best_score / 100, 0.0), 1.0),
            2,
        )

        return {
            "risk_score": risk_score,
            "threat_type": threat_type,
            "confidence": confidence,
            "subsystem_scores": {
                "weights": weights,
                "rule": rule_scores,
                "ml": {k: float(v) for k, v in ml_probs.items()},
                "rag": rag_scores,
                "fused": fused_per_class,
            },
            "fusion_reasoning": fusion_reasoning,
        }
