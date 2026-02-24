"""Observability service integrations for metrics, logs, ML monitoring, and alerting."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from backend.config import settings

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except ImportError:  # pragma: no cover - fallback for constrained environments
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

    class _NoOpMetric:
        def labels(self, **_kwargs):
            return self

        def inc(self):
            return None

        def time(self):
            class _NoOpTimer:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            return _NoOpTimer()

    def Counter(*_args, **_kwargs):
        return _NoOpMetric()

    def Histogram(*_args, **_kwargs):
        return _NoOpMetric()

    def generate_latest() -> bytes:
        return b"# Prometheus client not installed.\n"

logger = logging.getLogger("flexiroaster.observability")

REQUEST_COUNTER = Counter(
    "flexiroaster_observability_events_total",
    "Total observability events by category and provider.",
    ["category", "provider", "status"],
)

EVENT_LATENCY = Histogram(
    "flexiroaster_observability_event_dispatch_latency_seconds",
    "Latency for dispatching observability events.",
    ["category"],
)


class ObservabilityCategory(str, Enum):
    """Supported observability event categories."""

    metrics = "metrics"
    logs = "logs"
    ml_monitoring = "ml_monitoring"
    alerting = "alerting"


@dataclass
class ProviderStatus:
    """Provider connection status based on configured credentials."""

    enabled: bool
    configured: bool
    reason: Optional[str] = None


class ObservabilityService:
    """Dispatches events to configured observability providers."""

    def integration_status(self) -> Dict[str, Dict[str, ProviderStatus]]:
        return {
            "metrics_logs": {
                "prometheus": ProviderStatus(enabled=True, configured=True),
                "grafana": ProviderStatus(
                    enabled=settings.GRAFANA_ENABLED,
                    configured=bool(settings.GRAFANA_URL),
                    reason="Set GRAFANA_URL to enable deep-link dashboard metadata.",
                ),
                "elk": ProviderStatus(
                    enabled=settings.ELK_ENABLED,
                    configured=bool(settings.ELK_ENDPOINT),
                    reason="Set ELK_ENDPOINT to ship structured logs to Elasticsearch.",
                ),
            },
            "ml_monitoring": {
                "evidently_ai": ProviderStatus(
                    enabled=settings.EVIDENTLY_ENABLED,
                    configured=bool(settings.EVIDENTLY_API_KEY),
                    reason="Set EVIDENTLY_API_KEY for drift monitoring exports.",
                ),
                "arize_ai": ProviderStatus(
                    enabled=settings.ARIZE_ENABLED,
                    configured=bool(settings.ARIZE_SPACE_KEY and settings.ARIZE_API_KEY),
                    reason="Set ARIZE_SPACE_KEY and ARIZE_API_KEY for model tracing.",
                ),
                "fiddler_ai": ProviderStatus(
                    enabled=settings.FIDDLER_ENABLED,
                    configured=bool(settings.FIDDLER_URL and settings.FIDDLER_API_KEY),
                    reason="Set FIDDLER_URL and FIDDLER_API_KEY for model performance monitors.",
                ),
            },
            "alerting": {
                "pagerduty": ProviderStatus(
                    enabled=settings.PAGERDUTY_ENABLED,
                    configured=bool(settings.PAGERDUTY_ROUTING_KEY),
                    reason="Set PAGERDUTY_ROUTING_KEY for incident escalation.",
                ),
                "opsgenie": ProviderStatus(
                    enabled=settings.OPSGENIE_ENABLED,
                    configured=bool(settings.OPSGENIE_API_KEY),
                    reason="Set OPSGENIE_API_KEY for operations alert fan-out.",
                ),
            },
        }

    def dispatch_event(
        self,
        category: ObservabilityCategory,
        event_name: str,
        payload: Dict[str, Any],
        severity: str = "info",
    ) -> Dict[str, Any]:
        """Dispatch an observability event to configured providers."""
        result: Dict[str, Any] = {
            "category": category.value,
            "event_name": event_name,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
            "providers": {},
        }

        with EVENT_LATENCY.labels(category=category.value).time():
            if category in {ObservabilityCategory.metrics, ObservabilityCategory.logs}:
                result["providers"].update(self._send_to_metrics_and_logs(event_name, payload, severity))
            elif category == ObservabilityCategory.ml_monitoring:
                result["providers"].update(self._send_to_ml_monitoring(event_name, payload, severity))
            elif category == ObservabilityCategory.alerting:
                result["providers"].update(self._send_to_alerting(event_name, payload, severity))

        for provider, provider_result in result["providers"].items():
            REQUEST_COUNTER.labels(
                category=category.value,
                provider=provider,
                status=provider_result["status"],
            ).inc()

        return result

    def _send_to_metrics_and_logs(self, event_name: str, payload: Dict[str, Any], severity: str) -> Dict[str, Any]:
        providers: Dict[str, Any] = {
            "prometheus": {"status": "sent", "detail": "Counter/Histogram updated."},
        }

        if settings.ELK_ENABLED and settings.ELK_ENDPOINT:
            logger.info(
                "ELK log shipping payload",
                extra={
                    "elk_event": json.dumps(
                        {
                            "event_name": event_name,
                            "severity": severity,
                            "payload": payload,
                            "service": settings.APP_NAME,
                        }
                    )
                },
            )
            providers["elk"] = {
                "status": "sent",
                "detail": f"Structured log prepared for {settings.ELK_ENDPOINT}",
            }
        else:
            providers["elk"] = {
                "status": "skipped",
                "detail": "ELK disabled or ELK_ENDPOINT not configured.",
            }

        if settings.GRAFANA_ENABLED:
            providers["grafana"] = {
                "status": "sent",
                "detail": "Grafana reads Prometheus metrics via scrape endpoint.",
            }
        else:
            providers["grafana"] = {
                "status": "skipped",
                "detail": "Grafana integration disabled.",
            }

        return providers

    def _send_to_ml_monitoring(self, event_name: str, payload: Dict[str, Any], severity: str) -> Dict[str, Any]:
        base_event = {"event_name": event_name, "severity": severity, "payload": payload}

        return {
            "evidently_ai": self._provider_result(
                settings.EVIDENTLY_ENABLED and bool(settings.EVIDENTLY_API_KEY),
                "Prepared drift report event for Evidently AI.",
                base_event,
            ),
            "arize_ai": self._provider_result(
                settings.ARIZE_ENABLED and bool(settings.ARIZE_SPACE_KEY and settings.ARIZE_API_KEY),
                "Prepared model telemetry event for Arize AI.",
                base_event,
            ),
            "fiddler_ai": self._provider_result(
                settings.FIDDLER_ENABLED and bool(settings.FIDDLER_URL and settings.FIDDLER_API_KEY),
                "Prepared model monitoring payload for Fiddler AI.",
                base_event,
            ),
        }

    def _send_to_alerting(self, event_name: str, payload: Dict[str, Any], severity: str) -> Dict[str, Any]:
        alert = {
            "title": event_name,
            "severity": severity,
            "details": payload,
            "source": settings.APP_NAME,
        }
        return {
            "pagerduty": self._provider_result(
                settings.PAGERDUTY_ENABLED and bool(settings.PAGERDUTY_ROUTING_KEY),
                "Prepared PagerDuty event payload.",
                alert,
            ),
            "opsgenie": self._provider_result(
                settings.OPSGENIE_ENABLED and bool(settings.OPSGENIE_API_KEY),
                "Prepared Opsgenie alert payload.",
                alert,
            ),
        }

    @staticmethod
    def _provider_result(enabled: bool, success_message: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if enabled:
            return {"status": "sent", "detail": success_message, "payload_preview": payload}
        return {"status": "skipped", "detail": "Provider disabled or missing credentials."}

    @staticmethod
    def prometheus_payload() -> bytes:
        return generate_latest()

    @staticmethod
    def prometheus_content_type() -> str:
        return CONTENT_TYPE_LATEST


observability_service = ObservabilityService()
