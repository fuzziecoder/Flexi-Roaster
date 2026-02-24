"""Internal communication layer supporting REST and gRPC."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict

from .contracts import InternalRequest, InternalResponse

try:
    import grpc  # type: ignore
except Exception:  # pragma: no cover - optional dependency fallback
    grpc = None


class ServiceTransport(ABC):
    """Transport abstraction for internal calls."""

    protocol: str

    @abstractmethod
    async def send(self, service_name: str, endpoint: str, request: InternalRequest) -> InternalResponse:
        """Send internal request and return normalized response."""


class RestTransport(ServiceTransport):
    """REST-based transport for service-to-service communication."""

    protocol = "rest"

    async def send(self, service_name: str, endpoint: str, request: InternalRequest) -> InternalResponse:
        import httpx

        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                endpoint,
                json=request.model_dump(mode="json"),
                headers={"X-Correlation-ID": request.correlation_id or ""},
            )
            response.raise_for_status()
            response_data = response.json() if response.content else {}

        return InternalResponse(
            success=True,
            service=service_name,
            protocol=self.protocol,
            action=request.action,
            data=response_data,
        )


class GrpcTransport(ServiceTransport):
    """gRPC-based transport placeholder for high-performance internal calls."""

    protocol = "grpc"

    async def send(self, service_name: str, endpoint: str, request: InternalRequest) -> InternalResponse:
        if grpc is None:
            raise RuntimeError(
                "gRPC transport requires grpcio to be installed. "
                "Install grpcio and grpcio-tools and generate stubs for production use."
            )

        # The production version should call generated protobuf stubs here.
        # We return a normalized response to keep the architecture testable.
        return InternalResponse(
            success=True,
            service=service_name,
            protocol=self.protocol,
            action=request.action,
            data={
                "endpoint": endpoint,
                "status": "grpc-transport-ready",
                "payload": request.payload,
            },
        )


class TransportRegistry:
    """Registry for selecting communication transport by protocol."""

    def __init__(self) -> None:
        self._transports: Dict[str, ServiceTransport] = {
            "rest": RestTransport(),
            "grpc": GrpcTransport(),
        }

    def get(self, protocol: str) -> ServiceTransport:
        normalized = protocol.lower()
        if normalized not in self._transports:
            raise ValueError(f"Unsupported protocol: {protocol}")
        return self._transports[normalized]
