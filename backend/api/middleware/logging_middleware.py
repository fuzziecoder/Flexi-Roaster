"""
Request/Response Logging Middleware for FlexiRoaster.

Logs request details, response times, status codes, and errors.
Supports request ID tracing and sensitive field redaction.

The logger is configured HERE (not in main.py) so it initialises
correctly inside every subprocess that uvicorn --reload spawns.
"""
import sys
import time
import uuid
import json
import logging
from typing import Any, Dict, Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from backend.config import settings


# ---------------------------------------------------------------------------
# Logger setup — self-contained so it works under uvicorn --reload
# ---------------------------------------------------------------------------
logger = logging.getLogger("flexiroaster.api")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger.propagate = False

if not logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))
    logger.addHandler(_handler)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
_SENSITIVE_FIELDS: Set[str] = set()


def _get_sensitive_fields() -> Set[str]:
    """Return the set of sensitive field names (cached)."""
    global _SENSITIVE_FIELDS
    if not _SENSITIVE_FIELDS:
        _SENSITIVE_FIELDS = {f.lower() for f in settings.SENSITIVE_FIELDS}
    return _SENSITIVE_FIELDS


def redact_sensitive_data(data: Any) -> Any:
    """Recursively redact sensitive fields from a data structure."""
    sensitive = _get_sensitive_fields()
    if isinstance(data, dict):
        return {
            k: "[REDACTED]" if k.lower() in sensitive else redact_sensitive_data(v)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [redact_sensitive_data(item) for item in data]
    return data


def _sanitize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Redact values of sensitive headers."""
    sensitive_headers = {"authorization", "cookie", "x-api-key", "api-key", "token"}
    return {
        k: "[REDACTED]" if k.lower() in sensitive_headers else v
        for k, v in headers.items()
    }


_STATUS_PHRASES = {
    200: "OK", 201: "Created", 204: "No Content",
    301: "Moved Permanently", 302: "Found", 304: "Not Modified",
    400: "Bad Request", 401: "Unauthorized", 403: "Forbidden",
    404: "Not Found", 405: "Method Not Allowed", 409: "Conflict",
    422: "Unprocessable Entity", 429: "Too Many Requests",
    500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable",
}


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs HTTP request/response details.

    Features
    --------
    - Request ID generation / propagation via X-Request-ID header
    - Request method, path, and query parameter logging
    - Response status code, timing (ms), and content length
    - Sensitive field redaction for request bodies
    - Configurable verbosity via settings
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Request ID
        request_id = request.headers.get("x-request-id", str(uuid.uuid4())[:8])

        # Timing
        start = time.perf_counter()

        # Request info
        method = request.method
        path = request.url.path
        query = str(request.query_params) if request.query_params else ""
        client = request.client.host if request.client else "unknown"

        request_line = f"{method} {path}"
        if query:
            request_line += f"?{query}"

        logger.info("req_id=%s | --> %s | client=%s", request_id, request_line, client)

        # Optional: log request body (POST/PUT/PATCH only)
        if settings.LOG_REQUEST_BODY and method in ("POST", "PUT", "PATCH"):
            try:
                body = await request.body()
                if body:
                    sanitized = redact_sensitive_data(json.loads(body))
                    logger.debug(
                        "req_id=%s | request_body=%s",
                        request_id, json.dumps(sanitized, default=str),
                    )
            except Exception:
                logger.debug("req_id=%s | request_body=[non-JSON]", request_id)

        # Optional: log sanitized headers at DEBUG level
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "req_id=%s | headers=%s",
                request_id, json.dumps(_sanitize_headers(dict(request.headers))),
            )

        # Process the request
        try:
            response = await call_next(request)

            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            status = response.status_code
            phrase = _STATUS_PHRASES.get(status, "")
            length = response.headers.get("content-length", "-")

            # Log level based on status code
            log_fn = logger.error if status >= 500 else (logger.warning if status >= 400 else logger.info)
            log_fn(
                "req_id=%s | <-- %s %s -> %d %s (%sms) [%s bytes]",
                request_id, method, path, status, phrase, duration_ms, length,
            )

            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.error(
                "req_id=%s | <-- %s %s -> 500 Internal Server Error (%sms) | error=%s",
                request_id, method, path, duration_ms, str(exc),
                exc_info=True,
            )
            raise
