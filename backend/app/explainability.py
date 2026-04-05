"""Explainability Layer - generates human-readable explanations."""


class ExplainabilityLayer:
    """
    Formats and combines explanations from all pipeline components
    into clear, non-technical, human-readable strings.
    """

    def generate(
        self,
        rule_explanations: list[str],
        rag_explanations: list[str],
        ml_label: str,
        ml_confidence: float,
        features: dict,
        fusion_reasoning: list[str] | None = None,
    ) -> list[str]:
        """
        Generate a combined list of human-readable explanations.
        Prioritizes clarity and actionability.
        """
        explanations = []

        # Add rule-based explanations (most interpretable)
        explanations.extend(rule_explanations)

        # Add RAG-based explanations (pattern matching)
        explanations.extend(rag_explanations)

        # Add ML insight (supplementary)
        if ml_label != "safe" and ml_confidence > 0.5:
            confidence_word = self._confidence_to_word(ml_confidence)
            explanations.append(
                f"AI classification model {confidence_word} identifies this content as '{ml_label}'"
            )

        if fusion_reasoning:
            for reason in fusion_reasoning:
                explanations.append(f"Fusion logic: {reason}")

        # If no explanations were generated but there are some signals
        if not explanations:
            max_score = max(
                features.get("phishing_score", 0),
                features.get("manipulation_score", 0),
                features.get("disinformation_score", 0),
            )
            if max_score > 0:
                explanations.append(
                    "Minor signals detected but insufficient for a clear classification"
                )
            else:
                explanations.append(
                    "No significant threats detected in this content"
                )

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for exp in explanations:
            if exp not in seen:
                seen.add(exp)
                unique.append(exp)

        return unique

    def _confidence_to_word(self, confidence: float) -> str:
        """Convert confidence score to human-readable word."""
        if confidence >= 0.9:
            return "strongly"
        elif confidence >= 0.7:
            return "likely"
        elif confidence >= 0.5:
            return "possibly"
        else:
            return "weakly"
