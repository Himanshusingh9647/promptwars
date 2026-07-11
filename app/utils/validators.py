"""
Input validation and sanitization utilities.

All user-submitted data MUST pass through these validators before
being used in GenAI prompts or stored. This module prevents:
- Prompt injection attacks
- XSS via malicious input
- Invalid data reaching business logic
"""

import re
from typing import Optional

import bleach

from app.utils.constants import (
    ALLOWED_LOCATION_PATTERN,
    LANGUAGE_MAP,
    MAX_FAMILY_SIZE,
    MAX_LOCATION_LENGTH,
    MAX_TEXT_INPUT_LENGTH,
    MIN_FAMILY_SIZE,
)


class ValidationError(Exception):
    """Raised when user input fails validation."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"Validation error on '{field}': {message}")


# --------------------------------------------------------------------------- #
#  Prompt Injection Patterns
# --------------------------------------------------------------------------- #
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|above|prior)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a)", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"<\s*script", re.IGNORECASE),
    re.compile(r"\{\{.*\}\}", re.IGNORECASE),
    re.compile(r"\$\{.*\}", re.IGNORECASE),
]


def sanitize_text_input(text: str, field_name: str = "input") -> str:
    """
    Sanitize a text input by stripping HTML, dangerous characters,
    and checking for prompt injection patterns.

    Args:
        text: Raw user input string.
        field_name: Name of the field for error reporting.

    Returns:
        Cleaned, safe text string.

    Raises:
        ValidationError: If the input contains injection patterns or is invalid.
    """
    if not isinstance(text, str):
        raise ValidationError(field_name, "Input must be a string.")

    # Strip HTML tags
    cleaned: str = bleach.clean(text, tags=[], strip=True)

    # Trim whitespace
    cleaned = cleaned.strip()

    if not cleaned:
        raise ValidationError(field_name, "Input cannot be empty.")

    if len(cleaned) > MAX_TEXT_INPUT_LENGTH:
        raise ValidationError(
            field_name,
            f"Input exceeds maximum length of {MAX_TEXT_INPUT_LENGTH} characters.",
        )

    # Check for prompt injection patterns
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(cleaned):
            raise ValidationError(
                field_name,
                "Input contains disallowed patterns.",
            )

    return cleaned


def validate_location(location: str) -> str:
    """
    Validate and sanitize a location input.

    Args:
        location: Raw location string from user.

    Returns:
        Validated, trimmed location string.

    Raises:
        ValidationError: If location is invalid.
    """
    cleaned: str = sanitize_text_input(location, field_name="location")

    if len(cleaned) > MAX_LOCATION_LENGTH:
        raise ValidationError(
            "location",
            f"Location exceeds maximum length of {MAX_LOCATION_LENGTH} characters.",
        )

    if not re.match(ALLOWED_LOCATION_PATTERN, cleaned):
        raise ValidationError(
            "location",
            "Location must contain only letters, spaces, hyphens, commas, and periods.",
        )

    return cleaned


def validate_family_size(size: object) -> int:
    """
    Validate the family size input.

    Args:
        size: Raw family size value (may be str or int).

    Returns:
        Validated integer family size.

    Raises:
        ValidationError: If size is out of range or not a valid integer.
    """
    try:
        family_size: int = int(size)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        raise ValidationError(
            "family_size",
            "Family size must be a valid integer.",
        )

    if family_size < MIN_FAMILY_SIZE or family_size > MAX_FAMILY_SIZE:
        raise ValidationError(
            "family_size",
            f"Family size must be between {MIN_FAMILY_SIZE} and {MAX_FAMILY_SIZE}.",
        )

    return family_size


def validate_language(language: str) -> str:
    """
    Validate the language code against supported languages.

    Args:
        language: ISO language code (e.g., 'en', 'hi').

    Returns:
        Validated language code.

    Raises:
        ValidationError: If language is not supported.
    """
    cleaned: str = language.strip().lower()

    if cleaned not in LANGUAGE_MAP:
        supported: str = ", ".join(sorted(LANGUAGE_MAP.keys()))
        raise ValidationError(
            "language",
            f"Unsupported language '{cleaned}'. Supported: {supported}.",
        )

    return cleaned


def validate_special_needs(needs: Optional[str]) -> str:
    """
    Validate and sanitize optional special needs input.

    Args:
        needs: Optional special needs description.

    Returns:
        Sanitized string, or 'None' if empty.

    Raises:
        ValidationError: If input contains dangerous patterns.
    """
    if not needs or not needs.strip():
        return "None"

    return sanitize_text_input(needs, field_name="special_needs")
