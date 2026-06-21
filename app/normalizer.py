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
    
    # Match Month Day (e.g., july 15, july 15th, july 15, 2020)
    month_day_match = re.match(
        r"^(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\.?\s+(\d+)(?:st|nd|rd|th)?(?:,?\s+\d{4})?$",
        val
    )
    if month_day_match:
        month = month_day_match.group(1).capitalize()
        # Abbreviation maps
        months_map = {
            "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", 
            "Jun": "June", "Jul": "July", "Aug": "August", "Sep": "September", 
            "Oct": "October", "Nov": "November", "Dec": "December"
        }
        month = months_map.get(month, month)
        day = int(month_day_match.group(2))
        return f"{month} {day}"
        
    # Match Day Month (e.g., 15 july, 15th of july)
    day_month_match = re.match(
        r"^(\d+)(?:st|nd|rd|th)?\s+(?:of\s+)?(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\.?$",
        val
    )
    if day_month_match:
        day = int(day_month_match.group(1))
        month = day_month_match.group(2).capitalize()
        months_map = {
            "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", 
            "Jun": "June", "Jul": "July", "Aug": "August", "Sep": "September", 
            "Oct": "October", "Nov": "November", "Dec": "December"
        }
        month = months_map.get(month, month)
        return f"{month} {day}"

    # Match numeric formats like MM/DD or MM-DD (ignoring year or keeping standard format)
    numeric_match = re.match(r"^(\d{1,2})[/-](\d{1,2})(?:[/-]\d{2,4})?$", val)
    if numeric_match:
        # Assume month/day or day/month. Let's do simple check:
        n1 = int(numeric_match.group(1))
        n2 = int(numeric_match.group(2))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        # If n1 <= 12 and n2 <= 31, assume MM/DD (US standard often used in conversational agents)
        if n1 <= 12 and n2 <= 31:
            return f"{months[n1 - 1]} {n2}"
        elif n2 <= 12 and n1 <= 31:
            return f"{months[n2 - 1]} {n1}"

    return raw_val.strip()

def normalize_value(prop_canonical: str, raw_val: str) -> str:
    cleaned = raw_val.strip()
    
    if prop_canonical == "birthday":
        return normalize_date(cleaned)
        
    # Check string canonical mappings
    mapping = VALUE_CANONICALIZATION.get(prop_canonical, {})
    return mapping.get(cleaned.lower(), cleaned)

def normalize_fact(raw_prop: str, raw_val: str) -> Tuple[str, str]:
    canonical_prop = normalize_property(raw_prop)
    canonical_val = normalize_value(canonical_prop, raw_val)
    return canonical_prop, canonical_val
