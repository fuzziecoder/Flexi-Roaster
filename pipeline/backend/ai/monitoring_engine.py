"""AI-powered pipeline monitoring engine for self-healing orchestration."""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean
from typing import Any, Deque, Dict, List, Optional


@dataclass
class ExecutionSignal:
    """Normalized execution telemetry from Supabase and execution logs."""

    execution_id: str
    pipeline_id: str
    status: str
    duration_seconds: float
    stage_failures: int
    retry_count: int
    throughput_per_minute: float
    latency_ms: float
    cpu_percent: float
    memory_percent: float
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class MonitoringSnapshot:
    """Current health state for one pipeline."""

    pipeline_id: str
    window_minutes: int
    sampled_events: int
    avg_duration_seconds: float
    failure_rate: float
    retry_frequency: float
    avg_cpu_percent: float
    avg_memory_percent: float
    avg_throughput_per_minute: float
    avg_latency_ms: float
    latency_spike_detected: bool
    throughput_drop_detected: bool
    dominant_error_patterns: List[Dict[str, Any]]
    generated_at: datetime = field(default_factory=datetime.utcnow)


class PipelineMonitoringEngine:
    """
    In-memory monitoring engine used by API workers.

    Data sources:
      1) Supabase execution table (historical records)
      2) execution logs (error pattern extraction)
      3) metrics stream (CPU, memory, throughput, latency)
    """

    def __init__(self, window_minutes: int = 30, max_events_per_pipeline: int = 2000):
        self.window_minutes = window_minutes
        self.max_events_per_pipeline = max_events_per_pipeline
        self._events: Dict[str, Deque[ExecutionSignal]] = {}

    def ingest(self, signal: ExecutionSignal) -> None:
        """Ingest normalized telemetry event."""
        queue = self._events.setdefault(
            signal.pipeline_id,
            deque(maxlen=self.max_events_per_pipeline),
        )
        queue.append(signal)
        self._prune_old(signal.pipeline_id)

    def ingest_supabase_execution(self, row: Dict[str, Any]) -> None:
        """Map a Supabase execution row to an internal signal."""
        self.ingest(
            ExecutionSignal(
                execution_id=str(row.get("id")),
                pipeline_id=str(row.get("pipeline_id")),
                status=str(row.get("status", "unknown")),
                duration_seconds=float(row.get("duration_seconds", 0.0) or 0.0),
                stage_failures=int(row.get("stage_failures", 0) or 0),
                retry_count=int(row.get("retry_count", 0) or 0),
                throughput_per_minute=float(row.get("throughput_per_minute", 0.0) or 0.0),
                latency_ms=float(row.get("latency_ms", 0.0) or 0.0),
                cpu_percent=float(row.get("cpu_percent", 0.0) or 0.0),
                memory_percent=float(row.get("memory_percent", 0.0) or 0.0),
                error_message=row.get("error_message"),
            )
        )

    def build_snapshot(self, pipeline_id: str) -> MonitoringSnapshot:
        """Generate health snapshot for dashboard and remediation services."""
        self._prune_old(pipeline_id)
        events = list(self._events.get(pipeline_id, []))

        if not events:
            return MonitoringSnapshot(
                pipeline_id=pipeline_id,
                window_minutes=self.window_minutes,
                sampled_events=0,
                avg_duration_seconds=0.0,
                failure_rate=0.0,
                retry_frequency=0.0,
                avg_cpu_percent=0.0,
                avg_memory_percent=0.0,
                avg_throughput_per_minute=0.0,
                avg_latency_ms=0.0,
                latency_spike_detected=False,
                throughput_drop_detected=False,
                dominant_error_patterns=[],
            )

        durations = [event.duration_seconds for event in events]
        failures = [event for event in events if event.status.lower() == "failed" or event.stage_failures > 0]
        retries = [event.retry_count for event in events]
        cpu_values = [event.cpu_percent for event in events]
        memory_values = [event.memory_percent for event in events]
        throughput_values = [event.throughput_per_minute for event in events]
        latency_values = [event.latency_ms for event in events]

        avg_throughput = mean(throughput_values)
        throughput_drop_detected = any(
            current < avg_throughput * 0.5 for current in throughput_values[-5:]
        ) if len(throughput_values) >= 5 else False

        avg_latency = mean(latency_values)
        latency_spike_detected = any(
            current > avg_latency * 2 for current in latency_values[-5:]
        ) if len(latency_values) >= 5 else False

        return MonitoringSnapshot(
            pipeline_id=pipeline_id,
            window_minutes=self.window_minutes,
            sampled_events=len(events),
            avg_duration_seconds=round(mean(durations), 3),
            failure_rate=round(len(failures) / len(events), 3),
            retry_frequency=round(sum(retries) / len(events), 3),
            avg_cpu_percent=round(mean(cpu_values), 3),
            avg_memory_percent=round(mean(memory_values), 3),
            avg_throughput_per_minute=round(avg_throughput, 3),
            avg_latency_ms=round(avg_latency, 3),
            latency_spike_detected=latency_spike_detected,
            throughput_drop_detected=throughput_drop_detected,
            dominant_error_patterns=self._extract_error_patterns(events),
        )

    def _extract_error_patterns(self, events: List[ExecutionSignal]) -> List[Dict[str, Any]]:
        errors = [event.error_message for event in events if event.error_message]
        if not errors:
            return []

        counts = Counter(errors)
        return [
            {"pattern": pattern, "count": count}
            for pattern, count in counts.most_common(5)
        ]

    def _prune_old(self, pipeline_id: str) -> None:
        queue = self._events.get(pipeline_id)
        if not queue:
            return

        cutoff = datetime.utcnow() - timedelta(minutes=self.window_minutes)
        while queue and queue[0].timestamp < cutoff:
            queue.popleft()


monitoring_engine = PipelineMonitoringEngine()
