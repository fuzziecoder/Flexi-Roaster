"""API route module exports."""

from api.routes import (
    ai_automation,
    executions,
    health,
    microservices,
    model_infra,
    monitoring,
    orchestration,
    pipelines,
)

__all__ = [
    "ai_automation",
    "executions",
    "health",
    "microservices",
    "model_infra",
    "monitoring",
    "orchestration",
    "pipelines",
]
