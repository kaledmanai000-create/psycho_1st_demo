"""Feature extractor - detects urgency, fear, suspicious URLs, emotional tone."""

import ipaddress
import re
from urllib.parse import urlparse
from typing import Any


# Multi-language keyword dictionaries (with Tunisian Derja)
URGENCY_WORDS = {
    "en": [
        "urgent", "immediately", "act now", "hurry", "limited time", "expires",
        "deadline", "last chance", "don't miss", "right now", "asap", "quick",
        "time is running out", "final warning", "only today", "expire soon",
        "wake up tunisia", "share before", "before they delete",
    ],
    "fr": [
        "urgent", "immédiatement", "agissez maintenant", "dépêchez-vous",
        "temps limité", "expire", "dernière chance", "vite", "tout de suite",
        "partagez avant", "réveillez-vous", "maintenant ou jamais",
        "ne ratez pas", "c'est maintenant", "avant qu'ils suppriment",
        "partagez massivement", "partagez d'urgence", "alerte rouge",
    ],
    "ar": [
        "عاجل", "فورا", "سارع", "محدود", "آخر فرصة", "الآن",
        # Tunisian Derja urgency
        "تو", "فيق", "اصحى", "اصحاو", "فيقوا", "قبل فوات الأوان",
        "قبل ما يفوت", "لازم تو", "هالوقت", "باقي 24 ساعة",
        "قبل ما يمسحوا", "قبل ما يتمسح", "شارك تو", "سجل تو",
        "الوقت يجري", "آخر فرصة", "يسكر غدوة", "خسرت حقك",
    ],
}

FEAR_PHRASES = {
    "en": [
        "your account will be closed", "unauthorized access", "security breach",
        "your data has been compromised", "suspicious activity", "verify your identity",
        "failure to respond", "legal action", "law enforcement", "you have been selected",
        "your computer is infected", "virus detected", "account suspended",
        "payment overdue", "arrest warrant", "your children's future",
        "children are in danger", "stealing your future",
    ],
    "fr": [
        "votre compte sera fermé", "accès non autorisé", "faille de sécurité",
        "activité suspecte", "vérifiez votre identité", "action en justice",
        "vos enfants sont en danger", "service sera coupé", "facture impayée",
        "le peuple souffre", "notre pays est en danger", "restez esclaves",
        "complice du silence", "honte à ceux",
    ],
    "ar": [
        "سيتم إغلاق حسابك", "نشاط مشبوه", "تحقق من هويتك",
        # Tunisian Derja fear phrases
        "ولادنا في خطر", "ولادكم في خطر", "بلادك تتهرس",
        "تونس في خطر", "الشعب يموت", "خطير", "تحذير خطير",
        "خاف على عايلتك", "فيه سموم", "راح يقطعوا", "حسابك يتسكر",
        "مشكل أمني", "تم تجميد", "تم تعليقه", "يسرقوا فلوسك",
        "فزع", "خوفتني", "ناس تموت", "الشعب المسكين",
        "مستقبلهم", "حقك ضاع", "راح يندم",
    ],
}

ANGER_TRIGGERS = [
    "outrageous", "shocking", "disgusting", "unbelievable", "they don't want you to know",
    "wake up", "share before deleted", "mainstream media won't tell you",
    "corruption exposed", "scandal", "betrayal", "cover-up",
    # Tunisian Derja anger/guilt/shame triggers
    "اصحى", "اصحاو", "فيق", "فيقوا", "عيب عليك", "حرام عليهم",
    "كفى صمت", "كفى استغلال", "ماتسكتش", "سكوتك خيانة",
    "خاين لبلادو", "شريك في الجريمة", "صادم", "فضيحة",
    "غضب الشعب", "الظلم", "يسرقوا", "تبيع البلاد",
    "ما حد يحكي", "ما حد يدافع", "الشعب ساكت",
    # French Tunisian anger triggers
    "réveillez-vous", "honte", "scandale", "mensonge",
    "on nous ment", "silence complice",
]

CREDENTIAL_REQUEST_PATTERNS = [
    r"(enter|provide|confirm|verify|update)\s+(your\s+)?(password|credit card|ssn|social security|bank|account)",
    r"(log\s*in|sign\s*in)\s+(to\s+)?(verify|confirm|secure)",
    r"click\s+(here|below|link)\s+to\s+(verify|confirm|update|secure)",
    # French credential requests
    r"(entrez|confirmez|vérifiez)\s+(vos\s+)?(coordonnées|identifiants|mot de passe|informations)",
    r"cliquez\s+(ici|sur ce lien)\s+(pour\s+)?(vérifier|confirmer|payer)",
    # Tunisian Derja credential requests
    r"(ادخل|أدخل|أرسل).*?(كلمة السر|معلومات|رقم|بطاقة|حساب|CIN)",
    r"(اضغط هنا|ادخل على الرابط)",
]

SUSPICIOUS_DOMAIN_PATTERNS = [
    r"[a-zA-Z0-9-]*(?:paypal|amazon|apple|google|microsoft|netflix|bank|secure)[a-zA-Z0-9-]*\.[a-z]{2,}",
    r"(?:login|account|verify|secure|update|confirm)[.-][a-zA-Z0-9-]+\.[a-z]{2,}",
    r"[a-zA-Z0-9]+\.(?:tk|ml|ga|cf|gq|xyz|top|buzz|club)\b",
    # Tunisian institution impersonation
    r"[a-zA-Z0-9-]*(?:poste|steg|sonede|bna|zitouna|amen|biat|ooredoo|tunisie.?telecom|edinar)[a-zA-Z0-9-]*\.[a-z]{2,}",
]

DISINFORMATION_INDICATORS = [
    "exposed", "they don't want you to see", "banned", "censored", "truth revealed",
    "what they're hiding", "mainstream media lies", "fake news", "hoax",
    "conspiracy", "secret plan", "deep state", "new world order",
    "miracle cure", "doctors hate this", "big pharma", "100% proven",
    "scientists baffled", "one weird trick",
    # Tunisian Derja disinformation markers
    "الحقيقة المخفية", "وثائق مسربة", "مؤامرة", "يخبيوها", "يخبيها عليك",
    "ما يحبوكش تعرفها", "الحقيقة اللي", "تخبي الحقيقة", "مثبت",
    "يشفي في أسبوع", "علاج طبيعي", "وصفة جدتي", "الأطباء يخبيوها",
    "فضيحة", "صادم", "الحقيقة الصادمة",
    # French Tunisian disinformation markers
    "vérité cachée", "on vous cache", "documents secrets", "révélation",
    "exclusif", "scandale sanitaire", "complot", "personne ne publie",
    "les médias cachent", "le gouvernement ment", "substances interdites",
]

PAYMENT_REQUEST_PATTERNS = [
    r"(pay|payment|transfer|wire|send)\s+(now|immediately|today)",
    r"(gift\s*card|crypto|bitcoin|usdt|voucher)",
    r"(payer|paiement|virement)\s+(immédiat|urgent|maintenant)",
    r"(ادفع|خلاص|حوّل|حول|دفع)\s*(الآن|تو|فورا|حالاً)?",
]

ACCOUNT_SUSPENSION_PATTERNS = [
    r"(account|profile|service)\s+(suspended|locked|restricted|disabled)",
    r"(compte|service)\s+(suspendu|bloqué|restreint)",
    r"(حسابك|الخدمة)\s*(متوقف|مجمّد|مجمد|معلّق|يتسكر)",
]

PRIZE_GIVEAWAY_PATTERNS = [
    r"(you\s+won|winner|congratulations|free\s+iphone|claim\s+your\s+prize)",
    r"(gagné|félicitations|cadeau\s+gratuit|réclamez\s+votre\s+prix)",
    r"(ربحت|مبروك|جائزة|هدية\s+مجانية|اربح)"
]

IMPERSONATION_PATTERNS = [
    r"(paypal|microsoft|google|apple|amazon|netflix|poste|steg|sonede|bna|zitouna|amen|biat)",
    r"(official|support\s+team|security\s+team|service\s+client|service\s+officiel)",
    r"(الدعم\s+الفني|الفريق\s+الرسمي|خدمة\s+الحرفاء|الجهة\s+الرسمية)",
]

SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "top", "xyz", "buzz", "click", "work", "shop", "site", "online"
}

BAIT_TERMS = {"login", "verify", "reset", "secure", "confirm", "signin", "unlock", "update"}


# Tunisian social pressure / guilt / identity manipulation patterns
SOCIAL_PRESSURE_PATTERNS = [
    # Guilt-tripping (Derja)
    "عيب عليك", "حرام عليهم", "عيب عليك تسكت",
    "ما عندكش ضمير", "اللي عندو ضمير",
    # Identity-based pressure ("if you're a real Tunisian...")
    "كل تونسي حر", "تونسي حقيقي", "كنت تونسي", "تحب تونس",
    "تحب بلادك", "يحب بلادو", "كتونسي",
    # Shaming into action
    "اللي ما يشاركش", "ما تشاركش", "ما ينفعش تسكت",
    "أنت تتفرج", "راك ساكت", "تبقى ساكت",
    # Tribalism / us-vs-them
    "هوما يسرقوا", "يضحك عليك", "عدوك", "خاين",
    "شريك في الجريمة", "يخبيها عليك",
    # Forced sharing demands
    "لازم يشارك", "لازم تشارك", "لازم الكل يعرف", "شاركوا",
    "شارك هالبوست", "شارك هالفيديو", "شارك هالرسالة", "شارك هالخبر",
    "شارك مع صحابك", "شارك مع الكل",
    # French social pressure
    "si vous êtes un vrai", "partagez si", "si vous aimez",
    "ne soyez pas complice", "faites entendre", "chaque tunisien doit",
    "si vous avez du courage",
    # Martyrdom / emotional guilt
    "الشعب يعاني", "ناس تعاني", "مسكين الشعب",
    "قلبي يوجعني", "كل أم تونسية", "يا أمهات تونس",
]


class FeatureExtractor:
    """Extracts threat-related features from preprocessed text."""

    def extract(self, preprocessed: dict) -> dict[str, Any]:
        """
        Extract all features from preprocessed text.
        Returns a structured feature dictionary with matched items.
        """
        text = preprocessed["cleaned_text"].lower()
        language = preprocessed.get("language", "en")
        urls = preprocessed.get("urls", [])

        features = {
            "urgency": self._detect_urgency(text, language),
            "fear": self._detect_fear(text, language),
            "anger": self._detect_anger(text),
            "social_pressure": self._detect_social_pressure(text),
            "credential_requests": self._detect_credential_requests(text),
            "payment_requests": self._detect_regex_matches(text, PAYMENT_REQUEST_PATTERNS, score_step=25),
            "account_suspension": self._detect_regex_matches(text, ACCOUNT_SUSPENSION_PATTERNS, score_step=20),
            "prize_giveaway": self._detect_regex_matches(text, PRIZE_GIVEAWAY_PATTERNS, score_step=20),
            "impersonation": self._detect_regex_matches(text, IMPERSONATION_PATTERNS, score_step=15),
            "suspicious_urls": self._detect_suspicious_urls(urls, text),
            "disinformation_indicators": self._detect_disinformation(text),
            "exclamation_density": self._exclamation_density(preprocessed["original_text"]),
            "caps_density": self._caps_density(preprocessed["original_text"]),
        }

        # Compute aggregate scores per category
        features["phishing_score"] = self._compute_phishing_score(features)
        features["manipulation_score"] = self._compute_manipulation_score(features)
        features["disinformation_score"] = self._compute_disinformation_score(features)

        return features

    def _detect_urgency(self, text: str, language: str) -> dict:
        # For Tunisian Derja, check both ar and en keywords
        if language == "tn_ar":
            words = URGENCY_WORDS.get("ar", []) + URGENCY_WORDS.get("en", []) + URGENCY_WORDS.get("fr", [])
        else:
            words = URGENCY_WORDS.get(language, []) + URGENCY_WORDS.get("en", [])
        matched = [w for w in words if w in text]
        return {"matched": matched, "score": min(len(matched) * 15, 100)}

    def _detect_fear(self, text: str, language: str) -> dict:
        # For Tunisian Derja, check both ar and en/fr keywords
        if language == "tn_ar":
            phrases = FEAR_PHRASES.get("ar", []) + FEAR_PHRASES.get("en", []) + FEAR_PHRASES.get("fr", [])
        else:
            phrases = FEAR_PHRASES.get(language, []) + FEAR_PHRASES.get("en", [])
        matched = [p for p in phrases if p in text]
        return {"matched": matched, "score": min(len(matched) * 20, 100)}

    def _detect_anger(self, text: str) -> dict:
        matched = [t for t in ANGER_TRIGGERS if t in text]
        return {"matched": matched, "score": min(len(matched) * 15, 100)}

    def _detect_social_pressure(self, text: str) -> dict:
        """Detect Tunisian social pressure, guilt-tripping, and identity manipulation."""
        matched = [p for p in SOCIAL_PRESSURE_PATTERNS if p in text]
        return {"matched": matched, "score": min(len(matched) * 20, 100)}

    def _detect_credential_requests(self, text: str) -> dict:
        return self._detect_regex_matches(text, CREDENTIAL_REQUEST_PATTERNS, score_step=30)

    def _detect_regex_matches(self, text: str, patterns: list[str], score_step: int) -> dict:
        matched = []
        for pattern in patterns:
            finds = re.findall(pattern, text, re.IGNORECASE)
            if finds:
                matched.append(pattern)
        return {"matched": matched, "score": min(len(matched) * score_step, 100)}

    def _normalize_url(self, url: str) -> str:
        if url.startswith("www."):
            return f"http://{url}"
        if re.match(r"^(?:\d{1,3}\.){3}\d{1,3}", url):
            return f"http://{url}"
        if not re.match(r"^[a-z]+://", url, re.IGNORECASE):
            return f"http://{url}"
        return url

    def _extract_host(self, parsed) -> str:
        return (parsed.hostname or "").strip(".").lower()

    def _url_risk_signals(self, url: str) -> list[str]:
        signals: list[str] = []
        try:
            parsed = urlparse(self._normalize_url(url))
            host = self._extract_host(parsed)
            if not host:
                return signals

            if host.startswith("xn--") or "xn--" in host:
                signals.append("punycode_domain")

            parts = host.split(".")
            if len(parts) >= 5:
                signals.append("excessive_subdomains")

            tld = parts[-1] if len(parts) > 1 else ""
            if tld in SUSPICIOUS_TLDS:
                signals.append(f"suspicious_tld:{tld}")

            try:
                ipaddress.ip_address(host)
                signals.append("ip_based_url")
            except ValueError:
                pass

            if any(term in host for term in BAIT_TERMS):
                signals.append("login_bait_in_domain")

            if "@" in parsed.netloc:
                signals.append("at_symbol_obfuscation")

            if re.search(r"(?:-|\d){4,}", host):
                signals.append("domain_token_anomaly")
        except Exception:
            return signals
        return signals

    def _detect_suspicious_urls(self, urls: list, text: str) -> dict:
        matched: list[str] = []
        signal_map: dict[str, list[str]] = {}

        normalized_urls = list(dict.fromkeys(urls))
        for url in normalized_urls:
            signals = self._url_risk_signals(url)
            if signals:
                signal_map[url] = signals
                matched.extend(signals)

        for pattern in SUSPICIOUS_DOMAIN_PATTERNS:
            finds = re.findall(pattern, text, re.IGNORECASE)
            if finds:
                matched.append(f"regex_pattern:{pattern}")

        unique = list(dict.fromkeys(matched))
        return {
            "matched": unique,
            "url_signals": signal_map,
            "score": min(len(unique) * 18, 100),
        }

    def _detect_disinformation(self, text: str) -> dict:
        matched = [ind for ind in DISINFORMATION_INDICATORS if ind in text]
        return {"matched": matched, "score": min(len(matched) * 15, 100)}

    def _exclamation_density(self, text: str) -> float:
        if not text:
            return 0.0
        return min(text.count("!") / max(len(text.split()), 1), 1.0)

    def _caps_density(self, text: str) -> float:
        if not text:
            return 0.0
        alpha_chars = [c for c in text if c.isalpha()]
        if not alpha_chars:
            return 0.0
        return sum(1 for c in alpha_chars if c.isupper()) / len(alpha_chars)

    def _compute_phishing_score(self, features: dict) -> float:
        score = (
            features["credential_requests"]["score"] * 0.4
            + features["suspicious_urls"]["score"] * 0.25
            + features["urgency"]["score"] * 0.15
            + features["fear"]["score"] * 0.1
            + features["payment_requests"]["score"] * 0.1
        )
        if features["impersonation"]["score"] > 0:
            score += 8
        if features["account_suspension"]["score"] > 0:
            score += 6
        if features["prize_giveaway"]["score"] > 0:
            score += 6
        return min(score, 100)

    def _compute_manipulation_score(self, features: dict) -> float:
        score = (
            features["fear"]["score"] * 0.25
            + features["urgency"]["score"] * 0.20
            + features["anger"]["score"] * 0.20
            + features["social_pressure"]["score"] * 0.25
            + features["exclamation_density"] * 50 * 0.05
            + features["caps_density"] * 50 * 0.05
        )
        if features["impersonation"]["score"] > 0 and features["urgency"]["score"] > 0:
            score += 5
        return min(score, 100)

    def _compute_disinformation_score(self, features: dict) -> float:
        score = (
            features["disinformation_indicators"]["score"] * 0.5
            + features["anger"]["score"] * 0.2
            + features["caps_density"] * 50 * 0.15
            + features["exclamation_density"] * 50 * 0.15
        )
        return min(score, 100)
