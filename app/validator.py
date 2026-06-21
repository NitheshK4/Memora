import re
from datetime import datetime
from typing import Optional
from app.models import ExtractedFact, ValidationResult

class Validator:
    def validate_fact(self, fact: ExtractedFact, canonical_property: str, value_canonical: str) -> ValidationResult:
        # Check for empty value
        if not value_canonical or not value_canonical.strip():
            return ValidationResult(is_valid=False, reason="Value cannot be empty", error_type="empty_value")

        # Property-specific validations
        if canonical_property == "birthday":
            return self._validate_birthday(value_canonical)

        return ValidationResult(is_valid=True)

    def _validate_birthday(self, birthday_val: str) -> ValidationResult:
        # Check if year is present and plausible
        # If the birthday has a 4-digit year, verify it
        year_match = re.search(r"\b(1\d{3}|2\d{3})\b", birthday_val)
        if year_match:
            year = int(year_match.group(1))
            current_year = datetime.now().year
            if year < current_year - 120:
                return ValidationResult(
                    is_valid=False, 
                    reason=f"Birth year {year} is temporally implausible (over 120 years ago)",
                    error_type="temporal_implausibility"
                )
            if year > current_year:
                return ValidationResult(
                    is_valid=False, 
                    reason=f"Birth year {year} is in the future",
                    error_type="temporal_implausibility"
                )

        return ValidationResult(is_valid=True)

validator = Validator()
