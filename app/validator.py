import re
from datetime import datetime
from typing import Optional
from app.models import ExtractedFact, ValidationResult
from app.utils import sanitize_input_text


class Validator:
    """
    Multi-rule validation engine for extracted facts.

    Performs type checking and plausibility guards before any fact
    is committed to the memory graph.
    """

    # Maximum allowed length for any single fact value
    MAX_VALUE_LENGTH = 512

    def validate_fact(
        self, fact: ExtractedFact, canonical_property: str, value_canonical: str
    ) -> ValidationResult:
        # Sanitize input text first
        value_canonical = sanitize_input_text(value_canonical)

        # ── Universal checks ─────────────────────────────────
        if not value_canonical or not value_canonical.strip():
            return ValidationResult(
                is_valid=False, reason="Value cannot be empty", error_type="empty_value"
            )

        if len(value_canonical) > self.MAX_VALUE_LENGTH:
            return ValidationResult(
                is_valid=False,
                reason=f"Value exceeds maximum length ({self.MAX_VALUE_LENGTH} chars)",
                error_type="value_too_long",
            )

        # Check for HTML/Script tag injection to prevent XSS/injection payloads
        if re.search(r"<[a-zA-Z/!][^>]*>", value_canonical):
            return ValidationResult(
                is_valid=False,
                reason="Value cannot contain HTML or script tags",
                error_type="html_injection",
            )

        # Reject values that are just numbers/symbols with no semantic meaning (except date types)
        from app.property_registry import registry
        prop_def = registry.get(canonical_property)
        if prop_def.expected_type != "date" and re.fullmatch(r"[\d\s\W]+", value_canonical):
            return ValidationResult(
                is_valid=False,
                reason="Value must contain at least one alphabetic character",
                error_type="non_semantic_value",
            )

        # ── Property-specific checks ────────────────────────
        property_validators = {
            "birthday": self._validate_birthday,
            "name": self._validate_name,
            "employer": self._validate_employer,
            "city": self._validate_city,
            "email": self._validate_email,
        }

        validator_fn = property_validators.get(canonical_property)
        if validator_fn:
            return validator_fn(value_canonical)

        return ValidationResult(is_valid=True)

    # ────────────────────────────────────────────────────────
    # Birthday validation
    # ────────────────────────────────────────────────────────
    def _validate_birthday(self, birthday_val: str) -> ValidationResult:
        year_match = re.search(r"\b(1\d{3}|2\d{3})\b", birthday_val)
        if year_match:
            year = int(year_match.group(1))
            current_year = datetime.now().year
            if year < current_year - 120:
                return ValidationResult(
                    is_valid=False,
                    reason=f"Birth year {year} is temporally implausible (over 120 years ago)",
                    error_type="temporal_implausibility",
                )
            if year > current_year:
                return ValidationResult(
                    is_valid=False,
                    reason=f"Birth year {year} is in the future",
                    error_type="temporal_implausibility",
                )

        return ValidationResult(is_valid=True)

    # ────────────────────────────────────────────────────────
    # Name validation
    # ────────────────────────────────────────────────────────
    def _validate_name(self, name_val: str) -> ValidationResult:
        if len(name_val.strip()) < 2:
            return ValidationResult(
                is_valid=False,
                reason="Name must be at least 2 characters",
                error_type="name_too_short",
            )
        if len(name_val.strip()) > 64:
            return ValidationResult(
                is_valid=False,
                reason="Name exceeds maximum length (64 chars)",
                error_type="name_too_long",
            )
        # Name should contain only letters, spaces, hyphens, apostrophes
        if not re.fullmatch(r"[A-Za-z\s'\-]+", name_val.strip()):
            return ValidationResult(
                is_valid=False,
                reason="Name contains invalid characters",
                error_type="name_invalid_chars",
            )
        return ValidationResult(is_valid=True)

    # ────────────────────────────────────────────────────────
    # Employer validation
    # ────────────────────────────────────────────────────────
    def _validate_employer(self, employer_val: str) -> ValidationResult:
        if len(employer_val.strip()) < 2:
            return ValidationResult(
                is_valid=False,
                reason="Employer name must be at least 2 characters",
                error_type="employer_too_short",
            )
        return ValidationResult(is_valid=True)

    # ────────────────────────────────────────────────────────
    # City validation
    # ────────────────────────────────────────────────────────
    def _validate_city(self, city_val: str) -> ValidationResult:
        if len(city_val.strip()) < 2:
            return ValidationResult(
                is_valid=False,
                reason="City name must be at least 2 characters",
                error_type="city_too_short",
            )
        # City should contain only letters, spaces, hyphens, periods
        if not re.fullmatch(r"[A-Za-z\s.\-']+", city_val.strip()):
            return ValidationResult(
                is_valid=False,
                reason="City name contains invalid characters",
                error_type="city_invalid_chars",
            )
        return ValidationResult(is_valid=True)

    # ────────────────────────────────────────────────────────
    # Email validation
    # ────────────────────────────────────────────────────────
    def _validate_email(self, email_val: str) -> ValidationResult:
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(pattern, email_val.strip()):
            return ValidationResult(
                is_valid=False,
                reason="Invalid email address format",
                error_type="email_invalid_format",
            )
        return ValidationResult(is_valid=True)


validator = Validator()
