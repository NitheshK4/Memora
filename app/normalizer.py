import re
from typing import Tuple

PROPERTY_SYNONYMS = {
    # employer
    "work": "employer",
    "workplace": "employer",
    "job": "employer",
    "company": "employer",
    "employer": "employer",
    
    # city
    "city": "city",
    "location": "city",
    "live": "city",
    "home": "city",
    "hometown": "city",
    
    # birthday
    "birthday": "birthday",
    "birthdate": "birthday",
    "born": "birthday",
    
    # dog_name
    "dog": "dog_name",
    "dog_name": "dog_name",
    "pet": "dog_name",
    "pet_name": "dog_name",
    
    # preference
    "preference": "preference",
    "like": "preference",
    "dislike": "preference",
    "love": "preference",
    "hate": "preference",
    
    # hobby
    "hobby": "hobby",
    "hobbies": "hobby",
    "interest": "hobby",

    # name
    "name": "name",
    "first_name": "name",
    "full_name": "name",

    # email
    "email": "email",
    "email_address": "email",
    "emailaddress": "email",
    "mail": "email",

    # phone
    "phone": "phone",
    "phone_number": "phone",
    "phonenumber": "phone",
    "telephone": "phone",
    "mobile": "phone",
}

VALUE_CANONICALIZATION = {
    "employer": {
        "google inc.": "Google",
        "google": "Google",
        "alphabet": "Google",
        "meta platforms": "Meta",
        "meta": "Meta",
        "facebook": "Meta",
        "microsoft corp": "Microsoft",
        "microsoft": "Microsoft",
        "apple inc": "Apple",
        "apple": "Apple",
    },
    "city": {
        "nyc": "New York",
        "new york city": "New York",
        "new york": "New York",
        "sf": "San Francisco",
        "san fran": "San Francisco",
        "san francisco": "San Francisco",
        "la": "Los Angeles",
        "los angeles": "Los Angeles",
        "boston": "Boston",
        "seattle": "Seattle",
        "london": "London",
    }
}

def normalize_property(raw_prop: str) -> str:
    cleaned = raw_prop.strip().lower().replace(" ", "_")
    return PROPERTY_SYNONYMS.get(cleaned, cleaned)

def normalize_date(raw_val: str) -> str:
    # Try parsing month + day formats (e.g. July 15th, 15 July, 07-15)
    # Simple normalizer for common expressions
    val = raw_val.strip().lower()
    
    # Month name mappings for normalization
    months_map = {
        "january": "January", "february": "February", "march": "March", "april": "April",
        "may": "May", "june": "June", "july": "July", "august": "August",
        "september": "September", "october": "October", "november": "November", "december": "December",
        "jan": "January", "feb": "February", "mar": "March", "apr": "April",
        "jun": "June", "jul": "July", "aug": "August", "sep": "September",
        "oct": "October", "nov": "November", "dec": "December"
    }

    # Match Month Day Year or Month Day (e.g., july 15, july 15th, july 15, 1990)
    month_day_match = re.match(
        r"^(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\.?\s+(\d+)(?:st|nd|rd|th)?(?:,?\s+(\d{4}))?$",
        val
    )
    if month_day_match:
        month = months_map.get(month_day_match.group(1)) or month_day_match.group(1).capitalize()
        day = int(month_day_match.group(2))
        year = month_day_match.group(3)
        if year:
            return f"{month} {day}, {year}"
        return f"{month} {day}"
        
    # Match Day Month Year or Day Month (e.g., 15 july, 15th of july, 15 july 1990)
    day_month_match = re.match(
        r"^(\d+)(?:st|nd|rd|th)?\s+(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\.?(?:\s+(\d{4}))?$",
        val
    )
    if day_month_match:
        day = int(day_month_match.group(1))
        month = months_map.get(day_month_match.group(2)) or day_month_match.group(2).capitalize()
        year = day_month_match.group(3)
        if year:
            return f"{month} {day}, {year}"
        return f"{month} {day}"

    # Match numeric formats:
    # 1. YYYY-MM-DD or YYYY/MM/DD
    iso_match = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})$", val)
    if iso_match:
        year = iso_match.group(1)
        m_idx = int(iso_match.group(2))
        day = int(iso_match.group(3))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        if 1 <= m_idx <= 12 and 1 <= day <= 31:
            return f"{months[m_idx - 1]} {day}, {year}"

    # 2. MM/DD/YYYY or DD/MM/YYYY or MM-DD-YYYY or DD-MM-YYYY
    numeric_match = re.match(r"^(\d{1,2})[/-](\d{1,2})[/-](\d{4})$", val)
    if numeric_match:
        n1 = int(numeric_match.group(1))
        n2 = int(numeric_match.group(2))
        year = numeric_match.group(3)
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        if n1 <= 12 and n2 <= 31:
            return f"{months[n1 - 1]} {n2}, {year}"
        elif n2 <= 12 and n1 <= 31:
            return f"{months[n2 - 1]} {n1}, {year}"

    # 3. MM/DD or DD/MM (without year)
    numeric_no_year_match = re.match(r"^(\d{1,2})[/-](\d{1,2})$", val)
    if numeric_no_year_match:
        n1 = int(numeric_no_year_match.group(1))
        n2 = int(numeric_no_year_match.group(2))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        if n1 <= 12 and n2 <= 31:
            return f"{months[n1 - 1]} {n2}"
        elif n2 <= 12 and n1 <= 31:
            return f"{months[n2 - 1]} {n1}"

    return raw_val.strip()

def normalize_value(prop_canonical: str, raw_val: str) -> str:
    cleaned = raw_val.strip()
    
    if prop_canonical == "birthday":
        return normalize_date(cleaned)

    if prop_canonical == "email":
        return cleaned.lower()

    if prop_canonical == "phone":
        is_intl = cleaned.startswith("+")
        digits = re.sub(r"\D", "", cleaned)
        return f"+{digits}" if is_intl else digits

    # Check string canonical mappings
    mapping = VALUE_CANONICALIZATION.get(prop_canonical, {})
    return mapping.get(cleaned.lower(), cleaned)

def normalize_fact(raw_prop: str, raw_val: str) -> Tuple[str, str]:
    canonical_prop = normalize_property(raw_prop)
    canonical_val = normalize_value(canonical_prop, raw_val)
    return canonical_prop, canonical_val
