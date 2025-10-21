"""
Logging Configuration for Rebellis backend.
Structured JSON and console logging.
"""

import logging
import logging.config
import sys
from src.core.config import settings


def setup_logging() -> None:
    """Configure global logging according to settings."""
    log_format = (
        "%(asctime)s | %(levelname)-7s | %(name)s:%(lineno)d | %(message)s"
        if settings.LOG_FORMAT == "text"
        else '{"time": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "line": %(lineno)d, "message": "%(message)s"}'
    )

    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": log_format, "datefmt": "%Y-%m-%d %H:%M:%S"}
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "root": {"level": settings.LOG_LEVEL, "handlers": ["console"]},
    }

    logging.config.dictConfig(log_config)
    logging.getLogger(__name__).info("📜 Logging configured (%s mode)", settings.LOG_FORMAT.upper())


# Initialize logging on import
setup_logging()
