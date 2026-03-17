import logging
import logging.config
import contextvars
from pythonjsonlogger import jsonlogger

correlation_id_var = contextvars.ContextVar("correlation_id", default="no-correlation-id")

class CorrelationIDFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_var.get()
        return True

def setup_logging(log_level: str = "INFO") -> None:

    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "correlation_id": {
                "()": CorrelationIDFilter,
            }
        },

        "formatters": {
            "json": {
                "()": jsonlogger.JsonFormatter,
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s %(correlation_id)s",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ",
                "rename_fields": {
                    "asctime": "timestamp",
                    "levelname": "level",
                    "name": "logger",
                }
            }
        },

        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "filters": ["correlation_id"],
                "stream": "ext://sys.stdout",
            }
        },
        "root": {
            "handlers": ["console"],
            "level": log_level,
        },

        "loggers": {
            "sqlalchemy.engine": {
                "level": "WARNING",
                "propagate": False
            },
            "celery": {
                "level": "INFO",
                "propagate": False
            },
        }
    })