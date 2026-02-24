"""Microservice definitions and topology metadata."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class ServiceDefinition:
    name: str
    rest_endpoint: str
    grpc_endpoint: str
    responsibilities: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)


class PipelineService(ServiceDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="pipeline-service",
            rest_endpoint="http://pipeline-service:8001/internal/pipelines",
            grpc_endpoint="pipeline-service:50051",
            responsibilities=["pipeline CRUD", "stage definitions", "pipeline validation"],
        )


class ExecutionService(ServiceDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="execution-service",
            rest_endpoint="http://execution-service:8002/internal/executions",
            grpc_endpoint="execution-service:50052",
            responsibilities=["run orchestration", "retry engine", "execution lifecycle"],
            depends_on=["pipeline-service"],
        )


class AIInsightsService(ServiceDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="ai-insights-service",
            rest_endpoint="http://ai-insights-service:8003/internal/insights",
            grpc_endpoint="ai-insights-service:50053",
            responsibilities=["failure prediction", "root cause analysis", "recommendations"],
            depends_on=["execution-service", "metrics-service"],
        )


class MetricsService(ServiceDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="metrics-service",
            rest_endpoint="http://metrics-service:8004/internal/metrics",
            grpc_endpoint="metrics-service:50054",
            responsibilities=["timeseries aggregation", "SLA/SLO metrics", "service telemetry"],
            depends_on=["execution-service"],
        )


class NotificationService(ServiceDefinition):
    def __init__(self) -> None:
        super().__init__(
            name="notification-service",
            rest_endpoint="http://notification-service:8005/internal/notifications",
            grpc_endpoint="notification-service:50055",
            responsibilities=["alerts", "webhook dispatch", "email/slack notifications"],
            depends_on=["execution-service", "ai-insights-service", "metrics-service"],
        )


def build_service_catalog() -> Dict[str, ServiceDefinition]:
    """Build service catalog used by orchestrator."""
    services = [
        PipelineService(),
        ExecutionService(),
        AIInsightsService(),
        MetricsService(),
        NotificationService(),
    ]
    return {service.name: service for service in services}
