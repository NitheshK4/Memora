import logging
from app.utils import setup_logging, logger

def test_logger_setup():
    assert logger.name == "memora"

def test_setup_logging_returns_configured_logger():
    test_logger = setup_logging()
    assert test_logger.name == "memora"
    root_logger = logging.getLogger()
    assert len(root_logger.handlers) >= 1
