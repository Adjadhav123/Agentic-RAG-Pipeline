import logging 
import logging.config


def configure_logging(level: str = "INFO") -> logging.Logger:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": (
                        "%(asctime)s | %(levelname)s | "
                        "%(name)s | %(message)s"
                    )
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {
                "level": level.upper(),
                "handlers": ["console"],
            },
        }
    )
    return logging.getLogger("agentic_rag")