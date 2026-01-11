"""
Metrics API routes.
Provides system metrics and historical data.
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List
import random

from backend.api.schemas import SystemMetricsResponse, MetricResponse, MetricsHistoryResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])

# Import storage from other routes
from backend.api.routes.pipelines import pipelines_db
from backend.api.routes.executions import executions_db


@router.get(
    "",
    response_model=SystemMetricsResponse,
    summary="Get current system metrics"
)
async def get_metrics():
    """
    Get current system metrics including:
    - CPU and memory usage
    - Pipeline throughput
    - Active executions
    - Failure rate
    - Success rate
    - Average duration
    """
    # Calculate metrics from executions
    all_executions = list(executions_db.values())
    
    # Active executions
    from backend.models.pipeline import ExecutionStatus
    active_executions = len([
        e for e in all_executions
        if e.status in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]
    ])
    
    # Success and failure rates
    completed_executions = [
        e for e in all_executions
        if e.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]
    ]
    
    if completed_executions:
        successful = len([e for e in completed_executions if e.status == ExecutionStatus.COMPLETED])
        success_rate = (successful / len(completed_executions)) * 100
        failure_rate = 100 - success_rate
    else:
        success_rate = 100.0
        failure_rate = 0.0
    
    # Average duration
    durations = [e.duration for e in completed_executions if e.duration is not None]
    avg_duration = sum(durations) / len(durations) if durations else 0.0
    
    # Pipeline throughput (executions in last minute)
    one_minute_ago = datetime.now() - timedelta(minutes=1)
    recent_executions = [
        e for e in all_executions
        if e.started_at >= one_minute_ago
    ]
    pipeline_throughput = len(recent_executions)
    
    # Simulated CPU and memory (would be real in production)
    cpu_usage = random.uniform(20, 80)
    memory_usage = random.uniform(30, 70)
    
    return SystemMetricsResponse(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        pipeline_throughput=pipeline_throughput,
        active_executions=active_executions,
        failure_rate=failure_rate,
        total_pipelines=len(pipelines_db),
        success_rate=success_rate,
        avg_duration=avg_duration,
        timestamp=datetime.now()
    )


@router.get(
    "/history",
    response_model=MetricsHistoryResponse,
    summary="Get historical metrics"
)
async def get_metrics_history(
    metric: str = "throughput",
    period: str = "1h"
):
    """
    Get historical metrics data.
    
    - **metric**: Metric name (throughput, cpu, memory, etc.)
    - **period**: Time period (1h, 24h, 7d, 30d)
    """
    # Parse period
    period_map = {
        "1h": timedelta(hours=1),
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    
    if period not in period_map:
        period = "1h"
    
    delta = period_map[period]
    end_time = datetime.now()
    start_time = end_time - delta
    
    # Generate sample historical data
    # In production, this would query from database
    metrics: List[MetricResponse] = []
    
    # Generate data points based on period
    if period == "1h":
        points = 12  # Every 5 minutes
        interval = timedelta(minutes=5)
    elif period == "24h":
        points = 24  # Every hour
        interval = timedelta(hours=1)
    elif period == "7d":
        points = 7  # Every day
        interval = timedelta(days=1)
    else:  # 30d
        points = 30  # Every day
        interval = timedelta(days=1)
    
    for i in range(points):
        timestamp = start_time + (interval * i)
        
        # Generate sample values based on metric type
        if metric == "throughput":
            value = random.uniform(800, 2200)
            unit = "req/min"
        elif metric == "cpu":
            value = random.uniform(20, 80)
            unit = "%"
        elif metric == "memory":
            value = random.uniform(30, 70)
            unit = "%"
        else:
            value = random.uniform(0, 100)
            unit = None
        
        metrics.append(MetricResponse(
            name=metric,
            value=value,
            unit=unit,
            timestamp=timestamp
        ))
    
    return MetricsHistoryResponse(
        metrics=metrics,
        period=period,
        start_time=start_time,
        end_time=end_time
    )
