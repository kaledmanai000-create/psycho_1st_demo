"""Rule-based detection engine - provides explainable threat detection."""


class RuleEngine:
    """
    Pattern-based rule engine for threat detection.
    Each rule returns human-readable explanations for full transparency.
    """

    def analyze(self, features: dict, preprocessed: dict) -> dict:
        """
        Apply all rules and return results with explanations.
        Returns: {threat_type, score, explanations}
        """
        explanations = []
        scores = {"phishing": 0.0, "manipulation": 0.0, "disinformation": 0.0}

        # --- Phishing Rules ---
        phishing_explanations = self._check_phishing(features, preprocessed)
        explanations.extend(phishing_explanations)
        scores["phishing"] = features.get("phishing_score", 0)

        # --- Manipulation Rules ---
        manipulation_explanations = self._check_manipulation(features)
        explanations.extend(manipulation_explanations)
        scores["manipulation"] = features.get("manipulation_score", 0)

        # --- Disinformation Rules ---
        disinfo_explanations = self._check_disinformation(features)
        explanations.extend(disinfo_explanations)
        scores["disinformation"] = features.get("disinformation_score", 0)

        # --- Tone/Style Rules ---
        style_explanations = self._check_style(features)
        explanations.extend(style_explanations)

        # Determine primary threat type
        threat_type = max(scores, key=scores.get)
        max_score = scores[threat_type]

        if max_score < 10:
            threat_type = "safe"

        return {
            "threat_type": threat_type,
            "scores": scores,
            "rule_score": max_score,
            "explanations": explanations,
        }

    def _check_phishing(self, features: dict, preprocessed: dict) -> list[str]:
        explanations = []

        # Credential request detection
        if features["credential_requests"]["score"] > 0:
            explanations.append(
                "Content requests sensitive credentials (passwords, bank details, or personal information)"
            )

        # Suspicious URL detection
        suspicious_urls = features["suspicious_urls"]["matched"]
        if suspicious_urls:
            for url in suspicious_urls[:3]:
                explanations.append(f"Suspicious domain detected: '{url}' - may impersonate a trusted website")

        # URL + urgency combination (strong phishing signal)
        if features["suspicious_urls"]["score"] > 0 and features["urgency"]["score"] > 0:
            explanations.append(
                "Combination of suspicious links and urgency language is a strong phishing indicator"
            )

        # Fear + credential request (strong phishing signal)
        if features["fear"]["score"] > 0 and features["credential_requests"]["score"] > 0:
            explanations.append(
                "Uses fear tactics to pressure you into providing personal information"
            )

        return explanations

    def _check_manipulation(self, features: dict) -> list[str]:
        explanations = []

        # Social pressure / guilt-tripping detection (Tunisian patterns)
        social_matched = features.get("social_pressure", {}).get("matched", [])
        if social_matched:
            patterns_str = "', '".join(social_matched[:4])
            explanations.append(
                f"Psychological manipulation detected - social pressure tactics: '{patterns_str}' "
                f"- uses guilt, shame, or identity to force action"
            )

        # Combined social pressure + urgency = strong manipulation
        if (features.get("social_pressure", {}).get("score", 0) > 0 and
                features["urgency"]["score"] > 0):
            explanations.append(
                "Combines social pressure with urgency - a strong psychological manipulation pattern"
            )

        # Urgency detection
        urgency_matched = features["urgency"]["matched"]
        if urgency_matched:
            words_str = "', '".join(urgency_matched[:5])
            explanations.append(f"Detected urgency language: '{words_str}' - designed to pressure quick action")

        # Fear detection
        fear_matched = features["fear"]["matched"]
        if fear_matched:
            phrases_str = "', '".join(fear_matched[:3])
            explanations.append(f"Fear-based phrases detected: '{phrases_str}' - intended to cause panic")

        # Anger triggers
        anger_matched = features["anger"]["matched"]
        if anger_matched:
            triggers_str = "', '".join(anger_matched[:3])
            explanations.append(f"Anger-inducing language found: '{triggers_str}' - designed to provoke emotional reaction")

        # Multiple manipulation vectors = high confidence
        active_vectors = sum([
            1 if features.get("social_pressure", {}).get("score", 0) > 0 else 0,
            1 if features["urgency"]["score"] > 0 else 0,
            1 if features["fear"]["score"] > 0 else 0,
            1 if features["anger"]["score"] > 0 else 0,
        ])
        if active_vectors >= 3:
            explanations.append(
                "Multiple psychological manipulation techniques detected simultaneously "
                "(fear + urgency + social pressure) - high-confidence manipulation attempt"
            )

        return explanations

    def _check_disinformation(self, features: dict) -> list[str]:
        explanations = []

        disinfo_matched = features["disinformation_indicators"]["matched"]
        if disinfo_matched:
            indicators_str = "', '".join(disinfo_matched[:4])
            explanations.append(
                f"Disinformation indicators found: '{indicators_str}' - commonly used in misleading content"
            )

        # Sensationalist language pattern
        if len(disinfo_matched) >= 3:
            explanations.append(
                "High density of sensationalist language suggests unreliable or misleading content"
            )

        return explanations

    def _check_style(self, features: dict) -> list[str]:
        explanations = []

        if features["caps_density"] > 0.4:
            explanations.append(
                "Excessive use of CAPITAL LETTERS - often used to convey false urgency or aggression"
            )

        if features["exclamation_density"] > 0.3:
            explanations.append(
                "Excessive exclamation marks detected - a common tactic in sensationalist or scam content"
            )

        return explanations
