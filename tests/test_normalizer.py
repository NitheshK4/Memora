import pytest
from app.normalizer import (
    normalize_property,
    normalize_date,
    normalize_value,
    normalize_fact
)

def test_normalize_property_synonyms():
    # Standard synonyms
    assert normalize_property("email_address") == "email"
    assert normalize_property("emailaddress") == "email"
    assert normalize_property("phone_number") == "phone"
    assert normalize_property("workplace") == "employer"
    assert normalize_property("live") == "city"
    
    # Capitalization and spaces
    assert normalize_property("  First Name  ") == "name"

def test_normalize_date_formats():
    # Month name + Day
    assert normalize_date("july 15th") == "July 15"
    assert normalize_date("15 of july") == "July 15"
    
    # ISO formats
    assert normalize_date("1990-07-15") == "July 15, 1990"
    assert normalize_date("1990/07/15") == "July 15, 1990"
    
    # Slashes with Year
    assert normalize_date("07/15/1990") == "July 15, 1990"
    assert normalize_date("15/07/1990") == "July 15, 1990"
    
    # Numeric no year
    assert normalize_date("07-15") == "July 15"
    assert normalize_date("15/07") == "July 15"

def test_normalize_value_canonicalization():
    # Employer canonicalization
    assert normalize_value("employer", "google inc.") == "Google"
    assert normalize_value("employer", "facebook") == "Meta"
    
    # City canonicalization
    assert normalize_value("city", "nyc") == "New York"
    assert normalize_value("city", "sf") == "San Francisco"

def test_normalize_email():
    assert normalize_value("email", "  TEST@Example.com  ") == "test@example.com"
    assert normalize_value("email", "alice+bob@domain.co.uk") == "alice+bob@domain.co.uk"

def test_normalize_phone():
    # International number (starts with +)
    assert normalize_value("phone", "+1 (555) 123-4567") == "+15551234567"
    # Local number (no + prefix)
    assert normalize_value("phone", "123-456-7890") == "1234567890"
    assert normalize_value("phone", " (999) 888 7777 ") == "9998887777"

def test_normalize_fact_helper():
    prop, val = normalize_fact("email_address", "  MYEMAIL@Example.com ")
    assert prop == "email"
    assert val == "myemail@example.com"
    
    prop2, val2 = normalize_fact("phone_number", "+1-800-555-0199")
    assert prop2 == "phone"
    assert val2 == "+18005550199"
