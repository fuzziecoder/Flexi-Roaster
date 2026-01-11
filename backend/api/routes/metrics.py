"""
Metrics API Routes
System and pipeline metrics using database
"""
import random
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.api.schemas import MetricsResponse, MetricsHistoryResponse
from backend.db.database import get_db
from backend.db import crud

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


def calculate_metrics(db: Session) -> MetricsResponse:
    """Calculate current system metrics from database"""
    # Get executions from database
    db_executions = crud.get_executions(db, limit=100)
    total_executions = len(db_executions)
    
    if total_executions == 0:
        return MetricsResponse(
            cpu=random.uniform(20, 40),
            memory=random.uniform(30, 50),
            throughput=0,
            active_executions=0,
            total_pipelines=0,
            success_rate=0,
            failure_rate=0,
            avg_duration=0,
            timestamp=datetime.utcnow()
        )
    
    # Calculate from actual executions
    completed = [e for e in db_executions if e.status == "completed"]
    failed = [e for e in db_executions if e.status == "failed"]
    running = [e for e in db_executions if e.status == "running"]
    
    total_completed = len(completed) + len(failed)
    success_rate = (len(completed) / total_completed * 100) if total_completed > 0 else 0
    failure_rate = (len(failed) / total_completed * 100) if total_completed > 0 else 0
    
    # Calculate average duration
    durations = [e.duration for e in completed if e.duration]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    # Simulate system metrics
    cpu = random.uniform(40, 80) if running else random.uniform(20, 40)
    memory = random.uniform(50, 70) if running else random.uniform(30, 50)
    
    # Get pipelines count
    db_pipelines = crud.get_pipelines(db)
    
    return MetricsResponse(
        cpu=round(cpu, 1),
        memory=round(memory, 1),
        throughput=round(total_executions / 60, 2),  # per minute
        active_executions=len(running),
        total_pipelines=len(db_pipelines),
        success_rate=round(success_rate, 1),
        failure_rate=round(failure_rate, 1),
        avg_duration=round(avg_duration, 2),
        timestamp=datetime.utcnow()
    )


@router.get("", response_model=MetricsResponse)
async def get_metrics(db: Session = Depends(get_db)):
    """Get current system metrics"""
    return calculate_metrics(db)


@router.get("/history", response_model=MetricsHistoryResponse)
async def get_metrics_history(hours: int = 24, db: Session = Depends(get_db)):
    """Get historical metrics"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=hours)
    
    # Generate sample historical data (will be replaced with actual DB queries)
    metrics_list: List[MetricsResponse] = []
    
    # Generate data points every hour
    current_time = start_time
    while current_time <= end_time:
        metrics_list.append(
            MetricsResponse(
                cpu=random.uniform(40, 80),
                memory=random.uniform(50, 70),
                throughput=random.uniform(10, 30),
                active_executions=random.randint(0, 5),
                total_pipelines=random.randint(5, 15),
                success_rate=random.uniform(85, 99),
                failure_rate=random.uniform(1, 15),
                avg_duration=random.uniform(30, 120),
                timestamp=current_time
            )
        )
        current_time += timedelta(hours=1)
    
    return MetricsHistoryResponse(
        metrics=metrics_list,
        start_time=start_time,
        end_time=end_time
    )
