"""Centralized logging helpers for shipping logs to Logstash/Elasticsearch."""
from __future__ import annotations

import json
import logging
import logging.handlers
from datetime import datetime, timezone

from backend.config import settings


class JsonTcpLogstashHandler(logging.handlers.SocketHandler):
    """Send structured JSON logs over TCP to a Logstash input."""

    def makePickle(self, record: logging.LogRecord) -> bytes:  # noqa: N802
        document = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "flexiroaster-backend",
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        return (json.dumps(document, default=str) + "\n").encode("utf-8")


def configure_logstash_logging() -> bool:
    """Attach a Logstash TCP handler to the API logger when enabled."""
    if not settings.ENABLE_LOGSTASH_LOGGING:
        return False

    logger = logging.getLogger("flexiroaster.api")
    for handler in logger.handlers:
        if isinstance(handler, JsonTcpLogstashHandler):
            return True

    handler = JsonTcpLogstashHandler(settings.LOGSTASH_HOST, settings.LOGSTASH_PORT)
    handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    logger.addHandler(handler)
    return True
