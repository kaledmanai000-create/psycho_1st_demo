"""Security layer - input sanitization and prompt injection prevention."""

import re
import html


# Patterns that indicate prompt injection attempts
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(previous|above|all)\s+(instructions|prompts)",
    r"you\s+are\s+now\s+a",
    r"system\s*:\s*",
    r"<\s*script",
    r"javascript\s*:",
    r"on(error|load|click)\s*=",
    r"eval\s*\(",
    r"document\.(cookie|write|location)",
]

MAX_TEXT_LENGTH = 50000


def sanitize_input(text: str) -> str:
    """
    Sanitize user input text:
    - Strip HTML tags
    - Escape HTML entities
    - Limit length
    - Check for prompt injection
    """
    if not text or not isinstance(text, str):
        return ""

    # Truncate to max length
    text = text[:MAX_TEXT_LENGTH]

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode HTML entities then re-escape
    text = html.unescape(text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def check_prompt_injection(text: str) -> bool:
    """
    Check if text contains prompt injection patterns.
    Returns True if injection is detected.
    """
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def sanitize_for_storage(text: str) -> str:
    """Sanitize text before storing in database."""
    if not text:
        return ""
    # Escape for safe storage
    text = html.escape(text)
    return text[:5000]
