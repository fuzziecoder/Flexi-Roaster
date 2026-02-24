"""Monitoring endpoints for AI self-healing backend."""
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ai.monitoring_engine import monitoring_engine
from core.elasticsearch_client import elasticsearch_manager
from core.redis_services import redis_service_layer

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


@router.get("/logs/search", response_model=Dict[str, Any])
async def search_execution_logs(
    query: str,
    pipeline_id: str | None = None,
    execution_id: str | None = None,
    level: str | None = None,
    limit: int = 100,
):
    """Search indexed execution logs in Elasticsearch for fast filtering and analytics."""
    levels = [level] if level else None
    results = await elasticsearch_manager.search_logs(
        query=query,
        pipeline_id=pipeline_id,
        execution_id=execution_id,
        levels=levels,
        limit=limit,
    )
    return {"query": query, "count": len(results), "results": results}


@router.post("/cache/session/{session_id}", response_model=Dict[str, Any])
async def cache_session(session_id: str, payload: Dict[str, Any]):
    """Store session payload in Redis-backed session storage."""
    success = await redis_service_layer.set_session(session_id, payload)
    return {"success": success, "session_id": session_id}


@router.get("/cache/session/{session_id}", response_model=Dict[str, Any])
async def fetch_session(session_id: str):
    """Fetch session payload from Redis-backed session storage."""
    session = await redis_service_layer.get_session(session_id)
    return {"session_id": session_id, "session": session}


@router.post("/rate-limit/{identifier}", response_model=Dict[str, Any])
async def check_rate_limit(identifier: str):
    """Apply Redis-backed rate limiting check for an identifier."""
    return await redis_service_layer.check_rate_limit(identifier)


@router.post("/jobs/enqueue", response_model=Dict[str, Any])
async def enqueue_background_job(payload: Dict[str, Any]):
    """Push a background job payload into Redis list-based broker queue."""
    success = await redis_service_layer.enqueue_job(payload)
    return {"success": success}


@router.post("/jobs/dequeue", response_model=Dict[str, Any])
async def dequeue_background_job():
    """Pop a background job payload from Redis broker queue."""
    job = await redis_service_layer.dequeue_job()
    return {"job": job, "found": job is not None}
