"""Orchestrator for coordinating internal microservice communication."""
from __future__ import annotations

from typing import Any, Dict, List

from .communication import TransportRegistry
from .contracts import InternalRequest, InternalResponse
from .services import build_service_catalog, ServiceDefinition


class MicroserviceOrchestrator:
    """Coordinates internal service calls over REST or gRPC."""

    def __init__(self) -> None:
        self._catalog = build_service_catalog()
        self._transports = TransportRegistry()

    def architecture(self) -> List[Dict[str, Any]]:
        """Get architecture metadata for all services."""
        payload: List[Dict[str, Any]] = []
        for service in self._catalog.values():
            payload.append(
                {
                    "name": service.name,
                    "responsibilities": service.responsibilities,
                    "depends_on": service.depends_on,
                    "endpoints": {
                        "rest": service.rest_endpoint,
                        "grpc": service.grpc_endpoint,
                    },
                }
            )
        return payload

    async def call(
        self,
        service_name: str,
        action: str,
        payload: Dict[str, Any],
        protocol: str = "rest",
        correlation_id: str | None = None,
    ) -> InternalResponse:
        """Call target service via selected protocol."""
        service = self._require_service(service_name)
        endpoint = service.rest_endpoint if protocol.lower() == "rest" else service.grpc_endpoint
        transport = self._transports.get(protocol)
        request = InternalRequest(action=action, payload=payload, correlation_id=correlation_id)
        return await transport.send(service_name, endpoint, request)

    def _require_service(self, service_name: str) -> ServiceDefinition:
        if service_name not in self._catalog:
            raise ValueError(f"Unknown service: {service_name}")
        return self._catalog[service_name]
