import logging
from app.utils import setup_logging, logger, truncate_string, sanitize_input_text

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

def test_sanitize_input_text():
    assert sanitize_input_text("") == ""
    assert sanitize_input_text(None) == ""
    assert sanitize_input_text("  hello   world  ") == "hello world"
    assert sanitize_input_text("hello\x00world\x07!") == "helloworld!"
    assert sanitize_input_text("hello\nworld\t!") == "hello\nworld !"

