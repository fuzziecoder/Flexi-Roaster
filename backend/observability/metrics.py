"""Prometheus metrics registry and helpers for runtime observability."""
from __future__ import annotations

import os
from dataclasses import dataclass
from time import perf_counter
from typing import Optional

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest


@dataclass
class _Timer:
    """Simple timing helper used by request and execution instrumentation."""

    started_at: float

    @classmethod
    def start(cls) -> "_Timer":
        return cls(started_at=perf_counter())

    def elapsed_seconds(self) -> float:
        return max(perf_counter() - self.started_at, 0.0)


class ObservabilityMetrics:
    """Holds Prometheus metric objects and provides update helpers."""

    def __init__(self) -> None:
        self.http_requests_total = Counter(
            "flexiroaster_http_requests_total",
            "Total HTTP requests served",
            ["method", "path", "status"],
        )
        self.http_request_latency_seconds = Histogram(
            "flexiroaster_http_request_latency_seconds",
            "HTTP request latency in seconds",
            ["method", "path", "status"],
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
        )

        self.pipeline_executions_total = Counter(
            "flexiroaster_pipeline_executions_total",
            "Total number of pipeline execution outcomes",
            ["pipeline_id", "status"],
        )
        self.pipeline_execution_latency_seconds = Histogram(
            "flexiroaster_pipeline_execution_latency_seconds",
            "Pipeline execution latency in seconds",
            ["pipeline_id", "status"],
            buckets=(0.1, 0.5, 1, 2, 5, 10, 20, 30, 60, 120, 300, 600),
        )

        self.pipeline_failure_rate = Gauge(
            "flexiroaster_pipeline_failure_rate",
            "Pipeline failure rate as a percentage (0-100)",
            ["pipeline_id"],
        )
        self.pipeline_sla_breach_total = Counter(
            "flexiroaster_pipeline_sla_breaches_total",
            "Count of executions that exceeded SLA target latency",
            ["pipeline_id"],
        )

        self.active_executions = Gauge(
            "flexiroaster_active_executions",
            "Number of active (pending/running) executions",
        )
        self.process_cpu_percent = Gauge(
            "flexiroaster_process_cpu_percent",
            "Process CPU usage percent",
        )
        self.process_memory_rss_bytes = Gauge(
            "flexiroaster_process_memory_rss_bytes",
            "Process resident memory usage in bytes",
        )

    @staticmethod
    def prometheus_payload() -> tuple[bytes, str]:
        """Return latest Prometheus exposition bytes and content type."""
        return generate_latest(), CONTENT_TYPE_LATEST

    @staticmethod
    def start_timer() -> _Timer:
        return _Timer.start()

    def observe_http_request(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        status = str(status_code)
        self.http_requests_total.labels(method=method, path=path, status=status).inc()
        self.http_request_latency_seconds.labels(method=method, path=path, status=status).observe(duration_seconds)

    def observe_execution_outcome(
        self,
        pipeline_id: str,
        status: str,
        duration_seconds: Optional[float],
        failure_rate_percent: float,
        sla_target_seconds: float,
    ) -> None:
        self.pipeline_executions_total.labels(pipeline_id=pipeline_id, status=status).inc()
        self.pipeline_failure_rate.labels(pipeline_id=pipeline_id).set(max(min(failure_rate_percent, 100.0), 0.0))

        if duration_seconds is not None:
            safe_duration = max(duration_seconds, 0.0)
            self.pipeline_execution_latency_seconds.labels(
                pipeline_id=pipeline_id,
                status=status,
            ).observe(safe_duration)
            if safe_duration > sla_target_seconds:
                self.pipeline_sla_breach_total.labels(pipeline_id=pipeline_id).inc()

    def set_active_executions(self, count: int) -> None:
        self.active_executions.set(max(count, 0))

    def observe_process_resources(self) -> None:
        """Capture CPU and memory usage from the current process when possible."""
        try:
            import resource

            memory_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            # Linux reports KB, macOS reports bytes. Normalize by checking magnitude.
            if memory_kb < 10_000_000:
                memory_bytes = int(memory_kb * 1024)
            else:
                memory_bytes = int(memory_kb)
            self.process_memory_rss_bytes.set(max(memory_bytes, 0))
        except Exception:
            pass

        try:
            import psutil  # optional dependency

            process = psutil.Process(os.getpid())
            self.process_cpu_percent.set(max(process.cpu_percent(interval=0.0), 0.0))
            self.process_memory_rss_bytes.set(max(process.memory_info().rss, 0))
        except Exception:
            # Fallback to system load average as coarse CPU signal.
            try:
                load1, _, _ = os.getloadavg()
                cpu_guess = max(load1 * 100.0, 0.0)
                self.process_cpu_percent.set(cpu_guess)
            except Exception:
                pass


observability_metrics = ObservabilityMetrics()
