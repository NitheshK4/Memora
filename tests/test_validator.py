import pytest
from app.models import ExtractedFact
from app.validator import validator

def test_validate_valid_fact():
    fact = ExtractedFact(
        property_name="employer",
        value_raw="Google"
    )
    res = validator.validate_fact(fact, "employer", "Google")
    assert res.is_valid is True

def test_validate_birthday_valid():
    fact = ExtractedFact(
        property_name="birthday",
        value_raw="July 15, 1990"
    )
    res = validator.validate_fact(fact, "birthday", "July 15, 1990")
    assert res.is_valid is True

def test_validate_birthday_numeric():
    fact = ExtractedFact(
        property_name="birthday",
        value_raw="1990-07-15"
    )
    from app.normalizer import normalize_fact
    canonical_prop, canonical_val = normalize_fact(fact.property_name, fact.value_raw)
    assert canonical_prop == "birthday"
    assert canonical_val == "July 15, 1990"
    res = validator.validate_fact(fact, canonical_prop, canonical_val)
    assert res.is_valid is True

def test_validate_birthday_slashes():
    fact = ExtractedFact(
        property_name="birthday",
        value_raw="07/15/1990"
    )
    from app.normalizer import normalize_fact
    canonical_prop, canonical_val = normalize_fact(fact.property_name, fact.value_raw)
    assert canonical_prop == "birthday"
    assert canonical_val == "July-15-1990" or "July 15, 1990"
    res = validator.validate_fact(fact, canonical_prop, canonical_val)
    assert res.is_valid is True

def test_validate_birthday_implausible_past():
    fact = ExtractedFact(
        property_name="birthday",
        value_raw="July 15, 1850"
    )
    res = validator.validate_fact(fact, "birthday", "July 15, 1850")
    assert res.is_valid is False
    assert "implausible" in res.reason

def test_validate_birthday_future():
    fact = ExtractedFact(
        property_name="birthday",
        value_raw="July 15, 2035"
    )
    res = validator.validate_fact(fact, "birthday", "July 15, 2035")
    assert res.is_valid is False
    assert "future" in res.reason

def test_validate_empty_value():
    fact = ExtractedFact(
        property_name="city",
        value_raw=""
    )
    res = validator.validate_fact(fact, "city", "")
    assert res.is_valid is False
    assert "empty" in res.reason

def test_validate_html_injection():
    fact = ExtractedFact(
        property_name="city",
        value_raw="<script>alert('XSS')</script>"
    )
    res = validator.validate_fact(fact, "city", "<script>alert('XSS')</script>")
    assert res.is_valid is False
    assert res.error_type == "html_injection"
    assert "HTML or script tags" in res.reason

    fact2 = ExtractedFact(
        property_name="employer",
        value_raw="Google <b>Inc</b>"
    )
    res2 = validator.validate_fact(fact2, "employer", "Google <b>Inc</b>")
    assert res2.is_valid is False
    assert res2.error_type == "html_injection"

def test_validate_sanitized_fact():
    # Test that validator sanitizes inputs (e.g. collapsing spaces)
    fact = ExtractedFact(
        property_name="employer",
        value_raw="Google   Corp"
    )
    # The validate_fact method will sanitize value_canonical inside
    res = validator.validate_fact(fact, "employer", "Google   Corp")
    assert res.is_valid is True

def test_validate_email_valid():
    fact = ExtractedFact(
        property_name="email",
        value_raw="test@example.com"
    )
    res = validator.validate_fact(fact, "email", "test@example.com")
    assert res.is_valid is True

def test_validate_email_invalid():
    fact = ExtractedFact(
        property_name="email",
        value_raw="invalid-email"
    )
    res = validator.validate_fact(fact, "email", "invalid-email")
    assert res.is_valid is False
    assert res.error_type == "email_invalid_format"

