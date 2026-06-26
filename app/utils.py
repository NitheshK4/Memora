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

