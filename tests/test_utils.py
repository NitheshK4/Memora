import logging
from app.utils import setup_logging, logger, truncate_string

def test_logger_setup():
    assert logger.name == "memora"

def test_setup_logging_returns_configured_logger():
    test_logger = setup_logging()
    assert test_logger.name == "memora"
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) >= 1

def test_truncate_string():
    assert truncate_string("", 10) == ""
    assert truncate_string("hello", 10) == "hello"
    assert truncate_string("hello world", 5) == "hello..."
    assert truncate_string("hello  world", 6) == "hello..."

