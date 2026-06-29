import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("memora")

logger = setup_logging()

def truncate_string(text: str, max_len: int = 100) -> str:
    """Truncate a string to a maximum length, appending '...' if truncated."""
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[:max_len].strip() + "..."


def sanitize_input_text(text: str) -> str:
    """
    Sanitize input text by:
    1. Stripping leading/trailing whitespace.
    2. Removing non-printable control characters (except tabs and newlines).
    3. Collapsing multiple consecutive spaces into a single space.
    """
    if not text:
        return ""
    # Remove non-printable control characters
    cleaned = "".join(ch for ch in text if ord(ch) >= 32 or ch in "\n\r\t")
    # Collapse multiple consecutive spaces/tabs
    import re
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()

