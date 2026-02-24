"""API gateway-aware middleware for zero-trust edge controls."""
from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from backend.config import settings


class GatewayMiddleware(BaseHTTPMiddleware):
    """Validate trusted gateway headers and stamp governance metadata."""

    async def dispatch(self, request: Request, call_next):
        if settings.TRUSTED_GATEWAY_KEY:
            gateway_key = request.headers.get(settings.GATEWAY_KEY_HEADER)
            if gateway_key != settings.TRUSTED_GATEWAY_KEY:
                return JSONResponse(
                    status_code=401,
                    content={"error": "Unauthorized gateway", "detail": "Gateway signature mismatch"},
                )

        request.state.gateway = {
            "provider": settings.API_GATEWAY_PROVIDER,
            "request_id": request.headers.get("x-request-id"),
            "forwarded_for": request.headers.get("x-forwarded-for"),
        }

        response = await call_next(request)
        response.headers["X-API-Gateway"] = settings.API_GATEWAY_PROVIDER
        return response
