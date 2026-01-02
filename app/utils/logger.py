"""Logging configuration"""
import logging
import sys
from app.config import get_settings

settings = get_settings()

def setup_logger():
    logger = logging.getLogger("radiology_ai")
    logger.setLevel(getattr(logging, "INFO"))
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, "INFO"))

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()