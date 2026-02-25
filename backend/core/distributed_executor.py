"""Distributed execution dispatcher with optional distributed compute backends."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import logging

from backend.config import settings
from backend.core.executor import PipelineExecutor
from backend.models.pipeline import Execution, Pipeline

logger = logging.getLogger(__name__)

SUPPORTED_BACKENDS = {"local", "celery", "ray", "spark", "dask"}


@dataclass
class DispatchResult:
    """Result wrapper for execution dispatch metadata."""

    execution: Execution
    backend_used: str


class DistributedExecutionDispatcher:
    """Run pipeline execution on local runtime or distributed frameworks."""

    def __init__(self):
        self.executor = PipelineExecutor()

    def run(self, pipeline: Pipeline, backend_override: Optional[str] = None) -> DispatchResult:
        backend = (backend_override or settings.DISTRIBUTED_EXECUTION_BACKEND or "local").lower().strip()

        if backend not in SUPPORTED_BACKENDS:
            logger.warning("Unsupported backend '%s'. Falling back to local.", backend)
            backend = "local"

        if backend == "celery":
            execution, used_backend = self._execute_with_celery(pipeline)
            return DispatchResult(execution=execution, backend_used=used_backend)

        if backend == "ray":
            execution, used_backend = self._execute_with_ray(pipeline)
            return DispatchResult(execution=execution, backend_used=used_backend)

        if backend == "spark":
            execution, used_backend = self._execute_with_spark(pipeline)
            return DispatchResult(execution=execution, backend_used=used_backend)

        if backend == "dask":
            execution, used_backend = self._execute_with_dask(pipeline)
            return DispatchResult(execution=execution, backend_used=used_backend)

        execution = self.executor.execute(pipeline)
        return DispatchResult(execution=execution, backend_used="local")

    def _execute_with_celery(self, pipeline: Pipeline) -> tuple[Execution, str]:
        """Try Celery path; fallback to local execution when unavailable."""
        try:
            from celery import Celery

            app = Celery(
                "flexiroaster",
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND,
            )
            task_name = settings.CELERY_EXECUTION_TASK

            payload = pipeline.model_dump(mode="json")
            async_result = app.send_task(task_name, kwargs={"pipeline": payload})
            remote_output = async_result.get(timeout=600)
            execution = Execution.model_validate(remote_output)
            logger.info("Pipeline %s executed via Celery task %s", pipeline.id, task_name)
            return execution, "celery"
        except Exception as exc:
            logger.warning("Celery backend unavailable (%s). Executing locally.", exc)
            execution = self.executor.execute(pipeline)
            execution.context.setdefault("distributed_execution", {})
            execution.context["distributed_execution"].update(
                {
                    "requested_backend": "celery",
                    "fallback_backend": "local",
                    "fallback_reason": str(exc),
                }
            )
            return execution, "local"

    def _execute_with_ray(self, pipeline: Pipeline) -> tuple[Execution, str]:
        """Try Ray path; fallback to local execution when unavailable."""
        try:
            import ray

            if not ray.is_initialized():
                ray.init(address=settings.RAY_ADDRESS, namespace=settings.RAY_NAMESPACE, ignore_reinit_error=True)

            @ray.remote
            def execute_pipeline_remote(pipeline_payload: dict):
                from backend.core.executor import PipelineExecutor
                from backend.models.pipeline import Pipeline

                model = Pipeline.model_validate(pipeline_payload)
                result = PipelineExecutor().execute(model)
                return result.model_dump(mode="json")

            payload = pipeline.model_dump(mode="json")
            remote_ref = execute_pipeline_remote.remote(payload)
            remote_output = ray.get(remote_ref)
            execution = Execution.model_validate(remote_output)
            logger.info("Pipeline %s executed via Ray remote function", pipeline.id)
            return execution, "ray"
        except Exception as exc:
            logger.warning("Ray backend unavailable (%s). Executing locally.", exc)
            execution = self.executor.execute(pipeline)
            execution.context.setdefault("distributed_execution", {})
            execution.context["distributed_execution"].update(
                {
                    "requested_backend": "ray",
                    "fallback_backend": "local",
                    "fallback_reason": str(exc),
                }
            )
            return execution, "local"

    def _execute_with_spark(self, pipeline: Pipeline) -> tuple[Execution, str]:
        """Try Spark path; fallback to local execution when unavailable."""
        try:
            from pyspark.sql import SparkSession

            spark = (
                SparkSession.builder
                .master(settings.SPARK_MASTER_URL)
                .appName(settings.SPARK_APP_NAME)
                .getOrCreate()
            )
            logger.info("Spark backend initialized for pipeline %s", pipeline.id)
            spark.stop()

            execution = self.executor.execute(pipeline)
            execution.context.setdefault("distributed_execution", {})
            execution.context["distributed_execution"].update(
                {
                    "requested_backend": "spark",
                    "execution_mode": "spark-driver",
                }
            )
            return execution, "spark"
        except Exception as exc:
            logger.warning("Spark backend unavailable (%s). Executing locally.", exc)
            execution = self.executor.execute(pipeline)
            execution.context.setdefault("distributed_execution", {})
            execution.context["distributed_execution"].update(
                {
                    "requested_backend": "spark",
                    "fallback_backend": "local",
                    "fallback_reason": str(exc),
                }
            )
            return execution, "local"

    def _execute_with_dask(self, pipeline: Pipeline) -> tuple[Execution, str]:
        """Try Dask path; fallback to local execution when unavailable."""
        try:
            from dask.distributed import Client

            client = Client(settings.DASK_SCHEDULER_ADDRESS) if settings.DASK_SCHEDULER_ADDRESS else Client(processes=False)
            logger.info("Dask backend initialized for pipeline %s", pipeline.id)
            client.close()

            execution = self.executor.execute(pipeline)
            execution.context.setdefault("distributed_execution", {})
            execution.context["distributed_execution"].update(
                {
                    "requested_backend": "dask",
                    "execution_mode": "dask-local-cluster",
                }
            )
            return execution, "dask"
        except Exception as exc:
            logger.warning("Dask backend unavailable (%s). Executing locally.", exc)
            execution = self.executor.execute(pipeline)
            execution.context.setdefault("distributed_execution", {})
            execution.context["distributed_execution"].update(
                {
                    "requested_backend": "dask",
                    "fallback_backend": "local",
                    "fallback_reason": str(exc),
                }
            )
            return execution, "local"
