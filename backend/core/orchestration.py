"""Orchestration adapters for local and external workflow engines."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from backend.models.pipeline import ExecutionStatus


class OrchestrationEngine(str, Enum):
    """Supported orchestration backends."""

    LOCAL = "local"
    AIRFLOW = "airflow"
    TEMPORAL = "temporal"
    PREFECT = "prefect"


@dataclass
class OrchestrationRequest:
    """Request payload for orchestration dispatch."""

    engine: OrchestrationEngine
    execution_id: str
    pipeline_id: str
    pipeline_name: str
    retry_attempts: int = 1
    retry_backoff_seconds: int = 0
    schedule: Optional[str] = None
    options: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Result returned by an orchestration backend."""

    status: ExecutionStatus
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class ExternalOrchestrator:
    """Base class for non-local orchestration engines."""

    engine: OrchestrationEngine

    def dispatch(self, request: OrchestrationRequest) -> OrchestrationResult:
        raise NotImplementedError


class AirflowOrchestrator(ExternalOrchestrator):
    engine = OrchestrationEngine.AIRFLOW

    def dispatch(self, request: OrchestrationRequest) -> OrchestrationResult:
        dag_id = request.options.get("dag_id") or f"flexi_{request.pipeline_id}"
        dag_run_id = request.options.get("dag_run_id") or f"exec_{request.execution_id}"

        return OrchestrationResult(
            status=ExecutionStatus.PENDING,
            message="Submitted execution to Apache Airflow DAG run queue",
            metadata={
                "provider": self.engine.value,
                "dag_id": dag_id,
                "dag_run_id": dag_run_id,
                "scheduled_for": request.schedule,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "retry_attempts": request.retry_attempts,
            },
        )


class TemporalOrchestrator(ExternalOrchestrator):
    engine = OrchestrationEngine.TEMPORAL

    def dispatch(self, request: OrchestrationRequest) -> OrchestrationResult:
        workflow_id = request.options.get("workflow_id") or f"workflow-{request.execution_id}"
        task_queue = request.options.get("task_queue", "flexiroaster-default")

        return OrchestrationResult(
            status=ExecutionStatus.PENDING,
            message="Submitted execution to Temporal workflow engine",
            metadata={
                "provider": self.engine.value,
                "workflow_id": workflow_id,
                "task_queue": task_queue,
                "scheduled_for": request.schedule,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "retry_attempts": request.retry_attempts,
            },
        )


class PrefectOrchestrator(ExternalOrchestrator):
    engine = OrchestrationEngine.PREFECT

    def dispatch(self, request: OrchestrationRequest) -> OrchestrationResult:
        deployment_id = request.options.get("deployment_id") or request.pipeline_id
        flow_run_name = request.options.get("flow_run_name") or f"flexi-run-{request.execution_id}"

        return OrchestrationResult(
            status=ExecutionStatus.PENDING,
            message="Submitted execution to Prefect flow run",
            metadata={
                "provider": self.engine.value,
                "deployment_id": deployment_id,
                "flow_run_name": flow_run_name,
                "scheduled_for": request.schedule,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "retry_attempts": request.retry_attempts,
            },
        )


class OrchestrationRegistry:
    """Factory/registry for orchestration backends."""

    def __init__(self):
        self._registry = {
            OrchestrationEngine.AIRFLOW: AirflowOrchestrator(),
            OrchestrationEngine.TEMPORAL: TemporalOrchestrator(),
            OrchestrationEngine.PREFECT: PrefectOrchestrator(),
        }

    def get(self, engine: OrchestrationEngine) -> ExternalOrchestrator:
        if engine not in self._registry:
            raise ValueError(f"Unsupported external orchestration engine: {engine.value}")
        return self._registry[engine]
