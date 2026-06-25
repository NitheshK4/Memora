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
