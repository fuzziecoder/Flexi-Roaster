"""Enterprise orchestration capabilities for dynamic DAGs, event triggers, scaling and SLA checks."""
from __future__ import annotations

import asyncio
import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional

from config import settings

logger = logging.getLogger(__name__)

try:
    from kafka import KafkaConsumer
except Exception:  # pragma: no cover - optional dependency
    KafkaConsumer = None


@dataclass
class DynamicDAGSpec:
    """Structured output for generated/optimized DAG."""

    stages: List[Dict[str, Any]]
    parallel_groups: List[List[str]]
    strategy: str


class DynamicDAGGenerator:
    """Creates pipeline stage graphs from metadata descriptors."""

    DEFAULT_TYPES = {
        "extract": "input",
        "load": "output",
        "validate": "validation",
        "transform": "transform",
        "enrich": "transform",
        "publish": "output",
    }

    def generate(self, metadata: Dict[str, Any]) -> DynamicDAGSpec:
        raw_stages = metadata.get("stages") or []
        if not raw_stages:
            raise ValueError("metadata.stages is required for dynamic DAG generation")

        generated: List[Dict[str, Any]] = []
        stage_ids: List[str] = []
        for idx, source in enumerate(raw_stages, start=1):
            stage_id = source.get("id") or f"stage-{idx}"
            stage_ids.append(stage_id)
            intent = (source.get("intent") or source.get("type") or "transform").lower()
            generated.append(
                {
                    "id": stage_id,
                    "name": source.get("name") or stage_id.replace("-", " ").title(),
                    "type": self.DEFAULT_TYPES.get(intent, "transform"),
                    "config": source.get("config", {}),
                    "dependencies": list(source.get("depends_on", [])),
                    "timeout": source.get("timeout", settings.EXECUTOR_STAGE_TIMEOUT),
                    "max_retries": source.get("max_retries", settings.EXECUTOR_MAX_RETRIES),
                    "retry_delay": source.get("retry_delay", settings.EXECUTOR_RETRY_DELAY),
                    "is_critical": source.get("is_critical", True),
                }
            )

        # If metadata omits explicit dependencies, create a valid linear DAG.
        for idx, stage in enumerate(generated):
            if stage["dependencies"]:
                continue
            if idx > 0 and metadata.get("link_mode", "auto") == "auto":
                stage["dependencies"] = [generated[idx - 1]["id"]]

        groups = DependencyGraphOptimizer().build_parallel_groups(generated)
        return DynamicDAGSpec(stages=generated, parallel_groups=groups, strategy="metadata-driven")


class DependencyGraphOptimizer:
    """Optimizes dependency graphs with an AI-inspired heuristic for parallelism."""

    def optimize(self, stages: List[Dict[str, Any]]) -> DynamicDAGSpec:
        groups = self.build_parallel_groups(stages)
        optimized = self._sort_group_members(stages, groups)
        return DynamicDAGSpec(stages=optimized, parallel_groups=groups, strategy="ai-parallel-heuristic")

    def build_parallel_groups(self, stages: List[Dict[str, Any]]) -> List[List[str]]:
        graph = {s["id"]: set(s.get("dependencies", [])) for s in stages}
        groups: List[List[str]] = []
        done = set()

        while len(done) < len(graph):
            ready = [stage_id for stage_id, deps in graph.items() if stage_id not in done and deps.issubset(done)]
            if not ready:
                remaining = [stage_id for stage_id in graph if stage_id not in done]
                raise ValueError(f"Circular dependency detected for stages: {remaining}")
            groups.append(sorted(ready))
            done.update(ready)

        return groups

    def _sort_group_members(self, stages: List[Dict[str, Any]], groups: List[List[str]]) -> List[Dict[str, Any]]:
        stage_map = {stage["id"]: dict(stage) for stage in stages}
        ordered: List[Dict[str, Any]] = []

        for group in groups:
            # AI-inspired rank: high estimated workload starts first in the same parallel window.
            ranked = sorted(
                group,
                key=lambda sid: stage_map[sid].get("config", {}).get("estimated_load", 1),
                reverse=True,
            )
            ordered.extend(stage_map[sid] for sid in ranked)

        return ordered


class SLAMonitor:
    """Tracks stage SLA thresholds and emits alerts when violated."""

    def __init__(self, on_alert: Optional[Callable[[Dict[str, Any]], None]] = None):
        self._on_alert = on_alert

    def evaluate_stage(
        self,
        *,
        execution_id: str,
        pipeline_id: str,
        stage_id: str,
        duration_seconds: float,
        threshold_seconds: Optional[float],
    ) -> Optional[Dict[str, Any]]:
        threshold = threshold_seconds or settings.SLA_DEFAULT_STAGE_THRESHOLD_SECONDS
        if duration_seconds <= threshold:
            return None

        alert = {
            "event": "sla_violation",
            "execution_id": execution_id,
            "pipeline_id": pipeline_id,
            "stage_id": stage_id,
            "duration_seconds": duration_seconds,
            "threshold_seconds": threshold,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }
        if self._on_alert:
            self._on_alert(alert)
        logger.warning("SLA violation detected", extra={"alert": alert})
        return alert


class AutoScalingAdvisor:
    """Computes worker scale recommendations from queue pressure."""

    def recommend_workers(self, queue_size: int, active_workers: int) -> Dict[str, Any]:
        target = max(settings.WORKER_AUTOSCALING_MIN, active_workers)

        if queue_size > settings.WORKER_AUTOSCALING_SCALE_UP_THRESHOLD:
            extra = math.ceil(queue_size / max(1, settings.WORKER_AUTOSCALING_TARGET_QUEUE_PER_WORKER))
            target = min(settings.WORKER_AUTOSCALING_MAX, max(target, extra))
        elif queue_size < settings.WORKER_AUTOSCALING_SCALE_DOWN_THRESHOLD:
            target = max(settings.WORKER_AUTOSCALING_MIN, min(target, active_workers - 1))

        return {
            "queue_size": queue_size,
            "active_workers": active_workers,
            "recommended_workers": target,
            "scale_action": "up" if target > active_workers else "down" if target < active_workers else "steady",
        }


class KafkaExecutionTrigger:
    """Consumes Kafka trigger events and schedules pipeline execution callbacks."""

    def __init__(self):
        self._running = False

    async def consume(self, on_trigger: Callable[[Dict[str, Any]], Any]) -> None:
        if not settings.KAFKA_ENABLED or not settings.KAFKA_TRIGGER_ENABLED:
            logger.info("Kafka trigger listener disabled")
            return
        if KafkaConsumer is None:
            logger.warning("Kafka trigger enabled but kafka-python package unavailable")
            return

        consumer = KafkaConsumer(
            settings.KAFKA_TRIGGER_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id=settings.KAFKA_TRIGGER_GROUP,
            auto_offset_reset="latest",
            value_deserializer=lambda payload: json.loads(payload.decode("utf-8")),
            consumer_timeout_ms=1000,
        )

        self._running = True
        logger.info("Kafka trigger listener started")
        try:
            while self._running:
                for message in consumer:
                    event = message.value
                    await on_trigger(event)
                await asyncio.sleep(0.2)
        finally:
            consumer.close()
            logger.info("Kafka trigger listener stopped")

    def stop(self) -> None:
        self._running = False


__all__ = [
    "AutoScalingAdvisor",
    "DependencyGraphOptimizer",
    "DynamicDAGGenerator",
    "DynamicDAGSpec",
    "KafkaExecutionTrigger",
    "SLAMonitor",
]
