"""Observability endpoints for metrics, logs, ML monitoring, and alerting integrations."""
from datetime import datetime
from typing import Any, Dict, Literal

from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, Field

from backend.observability import ObservabilityCategory, observability_service

router = APIRouter(prefix="/observability", tags=["observability"])


class ObservabilityEventRequest(BaseModel):
    """Payload for sending observability events."""

    category: Literal["metrics", "logs", "ml_monitoring", "alerting"]
    event_name: str = Field(..., description="Human-readable event name")
    severity: Literal["debug", "info", "warning", "critical"] = "info"
    payload: Dict[str, Any] = Field(default_factory=dict)


@router.get("/integrations")
async def get_observability_integrations() -> Dict[str, Any]:
    """Return current observability integration status."""
    status = observability_service.integration_status()
    serialized = {
        domain: {provider: vars(details) for provider, details in providers.items()}
        for domain, providers in status.items()
    }
    return {"integrations": serialized, "timestamp": datetime.utcnow().isoformat()}


@router.get("/prometheus")
async def prometheus_metrics() -> Response:
    """Prometheus scrape endpoint."""
    return Response(
        content=observability_service.prometheus_payload(),
        media_type=observability_service.prometheus_content_type(),
    )


@router.post("/events")
async def dispatch_observability_event(request: ObservabilityEventRequest) -> Dict[str, Any]:
    """Dispatch structured events to configured observability providers."""
    category = ObservabilityCategory(request.category)
    return observability_service.dispatch_event(
        category=category,
        event_name=request.event_name,
        severity=request.severity,
        payload=request.payload,
    )
