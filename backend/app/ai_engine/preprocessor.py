"""Text preprocessor - cleaning and language detection."""

import re
import unicodedata


# French common words for language detection (including Tunisian French usage)
FRENCH_INDICATORS = {
    "le", "la", "les", "de", "du", "des", "un", "une", "et", "est",
    "en", "que", "qui", "dans", "pour", "pas", "sur", "avec", "ce",
    "sont", "nous", "vous", "ils", "elle", "mais", "ou", "donc",
    "avoir", "être", "faire", "dire", "aller", "voir", "savoir",
    "urgent", "attention", "gratuit", "cliquez", "compte", "banque",
    "vérifier", "confirmer", "sécurité", "mot", "passe", "connexion",
    "partagez", "tunisiens", "tunisie", "réveillez", "alerte",
    "facture", "votre", "immédiatement", "colis", "payer",
}

# Tunisian Derja indicators (common words that distinguish Derja from MSA)
DERJA_INDICATORS = {
    "باش", "ماشي", "متاعك", "متاعي", "متاعهم", "متاعها",
    "هال", "هاذي", "شنوة", "علاش", "كيفاش",
    "ياخي", "يزي", "برشا", "باهي",
    "تو", "اصحى", "فيق", "خلي بالك",
    "اضغط", "ادخل", "خلص", "خدمة",
    "ماتسكتش", "ماينفعش", "ماتخليش", "ماعندكش",
    "يلزمنا", "لازم", "نجموا", "نحبوا",
    "شارك", "شاركوا", "ولادنا", "بلادنا",
    "عباد", "صحابك", "عايلتك",
}

# Arabic Unicode range
ARABIC_RANGE = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+")


class Preprocessor:
    """Cleans and preprocesses text for analysis."""

    def clean_text(self, text: str) -> str:
        """Remove noise from text while preserving meaningful content."""
        if not text:
            return ""

        # Remove URLs but keep them for later analysis
        text_no_urls = re.sub(r"https?://\S+", " [URL] ", text)

        # Remove excessive special characters but keep punctuation
        text_clean = re.sub(r"[^\w\s.,!?;:'\"-@#$%&*()/\\]", " ", text_no_urls)

        # Normalize unicode
        text_clean = unicodedata.normalize("NFKD", text_clean)

        # Normalize whitespace
        text_clean = re.sub(r"\s+", " ", text_clean).strip()

        return text_clean

    def extract_urls(self, text: str) -> list[str]:
        """Extract all URLs from text."""
        url_pattern = re.compile(
            r"https?://[^\s<>\"']+|www\.[^\s<>\"']+|[a-zA-Z0-9-]+\.(com|org|net|bank|secure|login|account)[^\s<>\"']*"
        )
        return url_pattern.findall(text) if isinstance(text, str) else []

    def detect_language(self, text: str) -> str:
        """
        Detect language using heuristics.
        Returns: 'en', 'fr', 'tn_ar' (Tunisian Derja), or 'ar' (MSA)
        """
        if not text:
            return "en"

        # Check for Arabic characters
        arabic_chars = len(ARABIC_RANGE.findall(text))
        total_words = len(text.split())

        if arabic_chars > 0 and arabic_chars / max(total_words, 1) > 0.3:
            # Distinguish Tunisian Derja from MSA
            words = set(text.split())
            derja_matches = words.intersection(DERJA_INDICATORS)
            if len(derja_matches) >= 1:
                return "tn_ar"  # Tunisian Arabic (Derja)
            return "ar"  # Modern Standard Arabic

        # Check for French words
        words = set(text.lower().split())
        french_matches = words.intersection(FRENCH_INDICATORS)
        if len(french_matches) >= 3:
            return "fr"

        return "en"

    def preprocess(self, text: str) -> dict:
        """
        Full preprocessing pipeline.
        Returns dict with cleaned text, language, and extracted URLs.
        """
        urls = self.extract_urls(text)
        cleaned = self.clean_text(text)
        language = self.detect_language(text)

        return {
            "original_text": text,
            "cleaned_text": cleaned,
            "language": language,
            "urls": urls,
        }
