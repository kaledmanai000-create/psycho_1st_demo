"""RAG Engine - Retrieval Augmented Generation using FAISS for known threat patterns."""

import os
import json
import numpy as np
import faiss
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
PHISHING_PATTERNS_PATH = os.path.join(DATA_DIR, "phishing_patterns.json")
DISINFO_PATTERNS_PATH = os.path.join(DATA_DIR, "disinfo_patterns.json")
TRAINING_DATA_PATH = os.path.join(DATA_DIR, "training_data.json")


class RAGEngine:
    """
    Retrieval-Augmented Generation engine using FAISS.
    Compares input text against a database of known phishing and disinformation patterns.
    Uses TF-IDF vectors for lightweight, dependency-free similarity search.
    """

    def __init__(self):
        self.patterns: list[dict] = []
        self.pattern_texts: list[str] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.index: faiss.IndexFlatIP | None = None
        self._build_index()

    def _load_patterns(self) -> list[dict]:
        """Load known threat patterns from JSON files."""
        patterns = []

        for path, category in [
            (PHISHING_PATTERNS_PATH, "phishing"),
            (DISINFO_PATTERNS_PATH, "disinformation"),
        ]:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    item["category"] = category
                    item["source"] = os.path.basename(path)
                    patterns.append(item)

        # Add a curated subset of manipulation samples from the labeled dataset
        # to ensure retrieval can support all non-safe classes.
        if os.path.exists(TRAINING_DATA_PATH):
            with open(TRAINING_DATA_PATH, "r", encoding="utf-8") as f:
                train_data = json.load(f)
            for item in train_data:
                label = item.get("label")
                if label in {"phishing", "manipulation", "disinformation"}:
                    patterns.append({
                        "text": item.get("text", ""),
                        "category": label,
                        "template": f"train_{label}",
                        "source": "training_data.json",
                    })

        patterns = self._deduplicate_patterns(patterns)

        # Fallback patterns if no files exist
        if not patterns:
            patterns = self._get_default_patterns()

        return patterns

    def _deduplicate_patterns(self, patterns: list[dict]) -> list[dict]:
        seen = set()
        deduped = []
        for item in patterns:
            text = " ".join(str(item.get("text", "")).lower().split())
            key = (text, item.get("category", "unknown"))
            if not text or key in seen:
                continue
            seen.add(key)
            deduped.append(item)
        return deduped

    def _get_default_patterns(self) -> list[dict]:
        """Default patterns if no data files are available."""
        return [
            {"text": "Your account has been compromised. Click here to verify your identity immediately.", "category": "phishing", "template": "account_compromise"},
            {"text": "You have won a prize! Enter your bank details to claim your reward.", "category": "phishing", "template": "prize_scam"},
            {"text": "Urgent: Your payment failed. Update your credit card information now.", "category": "phishing", "template": "payment_failure"},
            {"text": "The government is hiding the truth. Share this before they delete it.", "category": "disinformation", "template": "conspiracy_share"},
            {"text": "Doctors don't want you to know about this miracle cure.", "category": "disinformation", "template": "miracle_cure"},
            {"text": "BREAKING: Secret documents reveal massive cover-up by officials.", "category": "disinformation", "template": "cover_up"},
        ]

    def _build_index(self):
        """Build FAISS index from known patterns."""
        self.patterns = self._load_patterns()
        self.pattern_texts = [p["text"] for p in self.patterns]

        if not self.pattern_texts:
            return

        # Use TF-IDF for vectorization (lightweight, no external model needed)
        self.vectorizer = TfidfVectorizer(
            max_features=6000,
            ngram_range=(1, 3),
            min_df=1,
            sublinear_tf=True,
            strip_accents="unicode",
        )
        tfidf_matrix = self.vectorizer.fit_transform(self.pattern_texts)

        # Convert to dense numpy array and normalize for cosine similarity
        vectors = tfidf_matrix.toarray().astype("float32")
        faiss.normalize_L2(vectors)

        # Build FAISS index (Inner Product = cosine similarity after normalization)
        dim = vectors.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(vectors)

    def search(self, text: str, top_k: int = 3) -> dict:
        """
        Search for similar known threat patterns.
        Returns: {matches, max_similarity, explanations}
        """
        if self.index is None or self.vectorizer is None:
            return {"matches": [], "max_similarity": 0.0, "explanations": []}

        # Vectorize query
        query_vec = self.vectorizer.transform([text]).toarray().astype("float32")
        faiss.normalize_L2(query_vec)

        # Search FAISS index
        scores, indices = self.index.search(query_vec, min(top_k, len(self.patterns)))

        matches = []
        explanations = []

        category_scores = {"phishing": 0.0, "manipulation": 0.0, "disinformation": 0.0}
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or score < 0.1:
                continue

            pattern = self.patterns[idx]
            match = {
                "pattern_text": pattern["text"][:100],
                "category": pattern["category"],
                "template": pattern.get("template", "unknown"),
                "similarity": float(score),
                "source": pattern.get("source", "unknown"),
            }
            matches.append(match)
            category_scores[pattern["category"]] = max(category_scores[pattern["category"]], float(score))

            if score >= 0.3:
                explanations.append(
                    f"Matches known {pattern['category']} pattern (template: {pattern.get('template', 'unknown')}, "
                    f"similarity: {score:.0%})"
                )

        max_sim = float(max(scores[0])) if len(scores[0]) > 0 else 0.0
        avg_sim = float(np.mean([m["similarity"] for m in matches])) if matches else 0.0
        # Combine max and average similarity to reduce one-off spurious match spikes.
        rag_score = min(max((0.65 * max_sim + 0.35 * avg_sim) * 100, 0.0), 100)

        return {
            "matches": matches,
            "max_similarity": max(max_sim, 0.0),
            "category_scores": category_scores,
            "explanations": explanations,
            "rag_score": rag_score,
        }
