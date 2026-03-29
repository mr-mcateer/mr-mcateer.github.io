"""
dlp.py -- Deterministic Data Loss Prevention Sanitizer

Fast, regex-based middleware that scrubs PII and sensitive data before
any text is sent to external APIs (Gemini, Anthropic, etc.).

Performance target: < 100ms on 10KB of text.
No LLM dependency. Pure regex pattern matching.

Usage:
    from dlp import sanitize, is_sensitive

    clean_text, redactions = sanitize("Student 123-45-6789 scored 85%")
    # clean_text: "Student [REDACTED:SSN] scored 85%"
    # redactions: [{"type": "SSN", "original": "123-45-6789", "position": 8}]
"""

import re
from typing import Optional

# Compiled regex patterns for speed (compiled once at import time)
_PATTERNS = [
    # SSN: 123-45-6789 or 123456789 (9 digits with optional dashes)
    ("SSN", re.compile(r'\b\d{3}-\d{2}-\d{4}\b')),
    ("SSN", re.compile(r'\b(?<!\d)\d{9}(?!\d)\b')),

    # Credit card numbers (13-19 digits, optionally separated by spaces or dashes)
    ("CREDIT_CARD", re.compile(
        r'\b(?:4\d{3}|5[1-5]\d{2}|3[47]\d{2}|6(?:011|5\d{2}))'
        r'[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{1,7}\b'
    )),

    # API keys and tokens (common prefixes)
    ("API_KEY", re.compile(r'\b(?:sk-[a-zA-Z0-9]{20,})\b')),
    ("API_KEY", re.compile(r'\b(?:ghp_[a-zA-Z0-9]{36,})\b')),
    ("API_KEY", re.compile(r'\b(?:xoxb-[a-zA-Z0-9\-]{20,})\b')),
    ("API_KEY", re.compile(r'\b(?:Bearer\s+[a-zA-Z0-9\-._~+/]{20,})\b')),
    ("API_KEY", re.compile(r'\b(?:AIza[a-zA-Z0-9\-_]{35})\b')),

    # Long hex/base64 strings that look like tokens (40+ chars)
    ("API_KEY", re.compile(r'\b[a-fA-F0-9]{40,}\b')),

    # Email addresses
    ("EMAIL", re.compile(
        r'\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}\b'
    )),

    # Phone numbers (US formats)
    ("PHONE", re.compile(
        r'\b(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b'
    )),

    # Student IDs (6-9 digit numbers standing alone, not part of dates or scores)
    ("STUDENT_ID", re.compile(
        r'(?<![/\-\d])\b\d{6,9}\b(?![/\-\d%])'
    )),

    # Medical: medication dosages
    ("MEDICATION", re.compile(
        r'\b\d+(?:\.\d+)?\s*(?:mg|mcg|ml|mL|IU|units?)\b', re.IGNORECASE
    )),

    # Medical: lab values (thyroid, diabetes markers)
    ("LAB_VALUE", re.compile(
        r'\b(?:TSH|T3|T4|A1C|HbA1c|fT3|fT4)\s*[=:]\s*\d+(?:\.\d+)?'
        r'(?:\s*(?:mIU/L|ng/dL|pmol/L|%))?\b', re.IGNORECASE
    )),

    # Financial: dollar amounts over $100 (with or without commas)
    ("FINANCIAL", re.compile(
        r'\$\s*(?:\d{1,3},)*\d{3,}(?:\.\d{2})?\b'
    )),

    # Bank routing numbers (9 digits following "routing" context)
    ("ROUTING_NUMBER", re.compile(
        r'(?:routing|ABA|transit)\s*(?:#|number|num|no\.?)?\s*:?\s*(\d{9})\b',
        re.IGNORECASE
    )),
]


def sanitize(text: str) -> tuple[str, list[dict]]:
    """
    Scan text for sensitive data patterns and replace with redaction tokens.

    Returns:
        tuple of (sanitized_text, list_of_redaction_records)
        Each redaction record: {"type": str, "original": str, "position": int}
    """
    if not text or not isinstance(text, str):
        return (text or "", [])

    redactions = []
    result = text

    for pattern_type, pattern in _PATTERNS:
        for match in pattern.finditer(result):
            # For ROUTING_NUMBER, capture group 1 is the actual number
            original = match.group(1) if match.lastindex else match.group(0)
            redactions.append({
                "type": pattern_type,
                "original": original,
                "position": match.start(),
            })

    # Apply redactions in reverse order to preserve positions
    for pattern_type, pattern in _PATTERNS:
        replacement = f"[REDACTED:{pattern_type}]"
        result = pattern.sub(replacement, result)

    return (result, redactions)


def is_sensitive(text: str) -> bool:
    """
    Quick check: does this text contain any sensitive patterns?
    Faster than sanitize() when you only need a boolean.
    """
    if not text or not isinstance(text, str):
        return False

    for _, pattern in _PATTERNS:
        if pattern.search(text):
            return True
    return False


def sanitize_parts(parts: list) -> list:
    """
    Sanitize a list of submission parts (mixed strings and PIL Images).
    Only processes string elements; images pass through unchanged.
    """
    sanitized = []
    for part in parts:
        if isinstance(part, str):
            clean, _ = sanitize(part)
            sanitized.append(clean)
        else:
            sanitized.append(part)
    return sanitized


if __name__ == "__main__":
    # Quick self-test
    tests = [
        ("SSN: 123-45-6789", "SSN: [REDACTED:SSN]"),
        ("Call 555-123-4567", "Call [REDACTED:PHONE]"),
        ("email test@example.com here", "email [REDACTED:EMAIL] here"),
        ("Token sk-abc123def456ghi789jkl012mno", None),
        ("TSH = 4.5 mIU/L", None),
        ("Take 50 mg levothyroxine", None),
        ("Invoice for $1,500.00", None),
    ]
    print("DLP Self-Test:")
    for input_text, expected in tests:
        result, redactions = sanitize(input_text)
        status = "PASS" if (expected is None or result == expected) else "FAIL"
        print(f"  {status}: {input_text!r} -> {result!r} ({len(redactions)} redactions)")
