"""Monitoring endpoints for AI self-healing backend."""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ai.monitoring_engine import monitoring_engine

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.post("/ingest", response_model=Dict[str, Any])
async def ingest_monitoring_event(payload: Dict[str, Any]):
    """Ingest telemetry from Supabase sync jobs, log processors, or metrics stream workers."""
    pipeline_id = payload.get("pipeline_id")
    if not pipeline_id:
        raise HTTPException(status_code=400, detail="pipeline_id is required")

    monitoring_engine.ingest_supabase_execution(payload)
    snapshot = monitoring_engine.build_snapshot(str(pipeline_id))

    return {
        "success": True,
        "pipeline_id": pipeline_id,
        "sampled_events": snapshot.sampled_events,
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/{pipeline_id}/snapshot", response_model=Dict[str, Any])
async def get_monitoring_snapshot(pipeline_id: str):
    """Get current risk and performance indicators for a pipeline."""
    snapshot = monitoring_engine.build_snapshot(pipeline_id)
    return {
        "pipeline_id": snapshot.pipeline_id,
        "window_minutes": snapshot.window_minutes,
        "sampled_events": snapshot.sampled_events,
        "metrics": {
            "avg_duration_seconds": snapshot.avg_duration_seconds,
            "failure_rate": snapshot.failure_rate,
            "retry_frequency": snapshot.retry_frequency,
            "avg_cpu_percent": snapshot.avg_cpu_percent,
            "avg_memory_percent": snapshot.avg_memory_percent,
            "avg_throughput_per_minute": snapshot.avg_throughput_per_minute,
            "avg_latency_ms": snapshot.avg_latency_ms,
        },
        "signals": {
            "latency_spike_detected": snapshot.latency_spike_detected,
            "throughput_drop_detected": snapshot.throughput_drop_detected,
            "dominant_error_patterns": snapshot.dominant_error_patterns,
        },
        "generated_at": snapshot.generated_at.isoformat(),
    }
