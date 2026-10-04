"""Component logs with safe structured fields and per-request correlation."""

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import UTC, datetime

request_id: ContextVar[str] = ContextVar("request_id", default="-")
SENSITIVE = (
    "authorization",
    "body",
    "credential",
    "password",
    "payload",
    "prompt",
    "secret",
    "signature",
    "token",
)


def safe_fields(fields):
    result = {}
    for key, value in fields.items():
        if any(marker in str(key).lower() for marker in SENSITIVE):
            result[str(key)] = "[redacted]"
        elif isinstance(value, dict):
            result[str(key)] = safe_fields(value)
        elif isinstance(value, (list, tuple)):
            result[str(key)] = f"List[{len(value)}]"
        elif isinstance(value, str):
            result[str(key)] = " ".join(value.split())[:200]
        elif value is None or isinstance(value, (int, float, bool)):
            result[str(key)] = value
        else:
            result[str(key)] = type(value).__name__
    return result


class AppFormatter(logging.Formatter):
    def __init__(self, mode="text"):
        super().__init__()
        self.mode = mode

    def format(self, record):
        entry = {
            "time": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "component": record.name,
            "event": record.getMessage(),
            "request_id": request_id.get(),
            "details": safe_fields(getattr(record, "details", {})),
        }
        # Exception messages can contain SQL parameters or credentials.
        if record.exc_info:
            entry["error_type"] = record.exc_info[0].__name__
        if self.mode == "json":
            return json.dumps(entry)
        return (
            " - ".join(
                str(entry[key]) for key in ("time", "level", "component", "event", "request_id")
            )
            + " - "
            + json.dumps(
                {key: value for key, value in entry.items() if key in ("details", "error_type")}
            )
        )


def configure_logging(level="INFO", mode="text"):
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"app": {"()": AppFormatter, "mode": mode}},
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "app",
                }
            },
            "root": {"handlers": ["stdout"], "level": level},
            "loggers": {
                "uvicorn": {"handlers": ["stdout"], "level": level, "propagate": False},
                "uvicorn.error": {"handlers": ["stdout"], "level": level, "propagate": False},
                # The request middleware logs route templates, never query strings or raw URLs.
                "uvicorn.access": {"handlers": [], "propagate": False},
                "httpx": {"level": "WARNING"},
                "httpcore": {"level": "WARNING"},
            },
        }
    )
