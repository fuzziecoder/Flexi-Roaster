"""
Distributed execution abstractions for FlexiRoaster.
Provides Celery task queue dispatch with optional Kafka event publishing.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from core.enterprise_orchestration import AutoScalingAdvisor

from config import settings

logger = logging.getLogger(__name__)

try:
    from celery import Celery
except Exception:  # pragma: no cover - optional dependency
    Celery = None

try:
    from kafka import KafkaProducer
except Exception:  # pragma: no cover - optional dependency
    KafkaProducer = None


class ExecutionDispatcher:
    """Dispatches execution jobs to queue backends and publishes events."""

    def __init__(self):
        self._celery_app: Optional[Celery] = None
        self._kafka_producer: Optional[KafkaProducer] = None
        self._autoscaling = AutoScalingAdvisor()

        if settings.EXECUTION_QUEUE_BACKEND == "celery" and Celery:
            self._celery_app = Celery(
                "flexiroaster_executor",
                broker=settings.CELERY_BROKER_URL,
                backend=settings.CELERY_RESULT_BACKEND,
            )
            self._celery_app.conf.task_default_queue = settings.CELERY_TASK_QUEUE
            logger.info("Celery dispatcher initialized")
        elif settings.EXECUTION_QUEUE_BACKEND == "celery":
            logger.warning("Celery backend requested but celery package is unavailable")

        if settings.KAFKA_ENABLED and KafkaProducer:
            self._kafka_producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda payload: json.dumps(payload).encode("utf-8"),
            )
            logger.info("Kafka producer initialized")
        elif settings.KAFKA_ENABLED:
            logger.warning("Kafka enabled but kafka-python package is unavailable")

    def enqueue_execution(
        self,
        pipeline_id: str,
        pipeline_name: str,
        stages: List[Dict[str, Any]],
        variables: Dict[str, Any],
        triggered_by: str,
    ) -> Dict[str, Any]:
        """Send execution request to queue backend and emit queued event."""
        payload = {
            "pipeline_id": pipeline_id,
            "pipeline_name": pipeline_name,
            "stages": stages,
            "variables": variables,
            "triggered_by": triggered_by,
        }

        task_ref: Optional[str] = None
        if self._celery_app:
            result = self._celery_app.send_task(settings.CELERY_TASK_NAME, kwargs=payload)
            task_ref = result.id
            logger.info("Queued pipeline execution in Celery", extra={"task_id": task_ref})

        self.publish_event("queued", payload, task_ref=task_ref)

        return {
            "accepted": True,
            "backend": settings.EXECUTION_QUEUE_BACKEND if self._celery_app else "inline",
            "task_id": task_ref,
        }

    def publish_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        *,
        task_ref: Optional[str] = None,
        execution_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> None:
        """Publish execution lifecycle event to Kafka when enabled."""
        if not self._kafka_producer:
            return

        event = {
            "event_type": event_type,
            "pipeline_id": payload.get("pipeline_id"),
            "pipeline_name": payload.get("pipeline_name"),
            "triggered_by": payload.get("triggered_by"),
            "task_id": task_ref,
            "execution_id": execution_id,
            "status": status,
        }
        self._kafka_producer.send(settings.KAFKA_EXECUTION_TOPIC, event)
        self._kafka_producer.flush(timeout=2)

    def queue_depth(self) -> int:
        """Best-effort queue depth for autoscaling signals."""
        inspect = self._celery_app.control.inspect() if self._celery_app else None
        if not inspect:
            return 0

        reserved = inspect.reserved() or {}
        scheduled = inspect.scheduled() or {}
        active = inspect.active() or {}

        return sum(len(items) for items in reserved.values()) + sum(len(items) for items in scheduled.values()) + sum(len(items) for items in active.values())

    def autoscaling_recommendation(self, active_workers: int) -> Dict[str, Any]:
        """Recommend worker count based on observed queue depth."""
        return self._autoscaling.recommend_workers(self.queue_depth(), active_workers)


execution_dispatcher = ExecutionDispatcher()
