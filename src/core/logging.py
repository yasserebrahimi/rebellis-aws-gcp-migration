import logging, logging.config, sys
from src.core.config import settings

def setup_logging():
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
        },
        "handlers": {
            "console": {"class": "logging.StreamHandler", "level": settings.LOG_LEVEL, "formatter": "standard", "stream": sys.stdout},
        },
        "root": {"level": settings.LOG_LEVEL, "handlers": ["console"]},
    }
    logging.config.dictConfig(log_config)
    logging.getLogger(__name__).info("Logging configured")
setup_logging()
