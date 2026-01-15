"""
Health and Metrics API Routes for FlexiRoaster.
Provides health checks and system metrics.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas import (
    HealthResponse, ServiceHealth, DashboardMetrics,
    AIInsightResponse, AIInsightListResponse
)
from db import (
    get_db_session, PipelineCRUD, ExecutionCRUD, AIInsightCRUD
)
from db.database import check_database_health
from core.redis_state import redis_state_manager
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check endpoint"
)
async def health_check(
    db: Session = Depends(get_db_session)
):
    """
    Check health of the application and all dependent services.
    
    Returns status of:
    - Application
    - Database
    - Redis
    """
    services = {}
    overall_status = "healthy"
    
    # Check database
    db_health = check_database_health()
    services["database"] = ServiceHealth(
        status=db_health.get("status", "unknown"),
        details=db_health
    )
    if db_health.get("status") != "healthy":
        overall_status = "degraded"
    
    # Check Redis
    redis_health = await redis_state_manager.health_check()
    services["redis"] = ServiceHealth(
        status=redis_health.get("status", "unknown"),
        latency_ms=redis_health.get("latency_ms"),
        details=redis_health
    )
    if redis_health.get("status") != "healthy":
        if redis_health.get("fallback_mode"):
            services["redis"].details["note"] = "Running in fallback mode"
        else:
            overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        app=settings.APP_NAME,
        version=settings.APP_VERSION,
        timestamp=datetime.now(),
        services=services
    )


@router.get(
    "/metrics",
    response_model=DashboardMetrics,
    summary="Get dashboard metrics"
)
async def get_dashboard_metrics(
    db: Session = Depends(get_db_session)
):
    """
    Get aggregated metrics for the dashboard.
    
    Returns:
    - Pipeline counts
    - Execution statistics
    - Recent high-severity insights
    """
    # Pipeline counts
    total_pipelines = PipelineCRUD.count(db)
    active_pipelines = PipelineCRUD.count(db, is_active=True)
    
    # Execution statistics (last 30 days)
    all_pipelines = PipelineCRUD.get_all(db)
    total_executions = 0
    successful_executions = 0
    failed_executions = 0
    total_duration = 0.0
    duration_count = 0
    
    for pipeline in all_pipelines:
        stats = ExecutionCRUD.get_stats(db, pipeline.id, days=30)
        total_executions += stats.get("total", 0)
        successful_executions += stats.get("completed", 0)
        failed_executions += stats.get("failed", 0)
        if stats.get("avg_duration", 0) > 0:
            total_duration += stats.get("avg_duration", 0)
            duration_count += 1
    
    success_rate = 0.0
    if total_executions > 0:
        success_rate = (successful_executions / total_executions) * 100
    
    avg_duration = 0.0
    if duration_count > 0:
        avg_duration = total_duration / duration_count
    
    # Recent insights
    recent_insights_db = AIInsightCRUD.get_recent_high_severity(db, hours=24, limit=5)
    recent_insights = [
        AIInsightResponse(
            id=i.id,
            pipeline_id=i.pipeline_id,
            execution_id=i.execution_id,
            stage_id=i.stage_id,
            insight_type=i.insight_type,
            severity=i.severity,
            title=i.title,
            message=i.message,
            recommendation=i.recommendation,
            confidence=i.confidence,
            risk_score=i.risk_score,
            factors=i.factors or [],
            explanation=i.explanation,
            action_taken=i.action_taken,
            is_resolved=i.is_resolved,
            created_at=i.created_at
        )
        for i in recent_insights_db
    ]
    
    return DashboardMetrics(
        total_pipelines=total_pipelines,
        active_pipelines=active_pipelines,
        total_executions=total_executions,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        success_rate=round(success_rate, 1),
        avg_duration=round(avg_duration, 2),
        recent_insights=recent_insights
    )


@router.get(
    "/insights",
    response_model=AIInsightListResponse,
    summary="Get AI insights"
)
async def get_insights(
    pipeline_id: str = None,
    execution_id: str = None,
    unresolved_only: bool = False,
    hours: int = 24,
    limit: int = 50,
    db: Session = Depends(get_db_session)
):
    """
    Get AI-generated insights.
    
    - **pipeline_id**: Filter by pipeline
    - **execution_id**: Filter by execution
    - **unresolved_only**: Only return unresolved insights
    - **hours**: Get insights from last N hours
    - **limit**: Maximum to return
    """
    if execution_id:
        insights_db = AIInsightCRUD.get_by_execution(db, execution_id)
    elif pipeline_id:
        insights_db = AIInsightCRUD.get_by_pipeline(
            db, pipeline_id, unresolved_only=unresolved_only, limit=limit
        )
    else:
        insights_db = AIInsightCRUD.get_recent_high_severity(db, hours=hours, limit=limit)
    
    insights = [
        AIInsightResponse(
            id=i.id,
            pipeline_id=i.pipeline_id,
            execution_id=i.execution_id,
            stage_id=i.stage_id,
            insight_type=i.insight_type,
            severity=i.severity,
            title=i.title,
            message=i.message,
            recommendation=i.recommendation,
            confidence=i.confidence,
            risk_score=i.risk_score,
            factors=i.factors or [],
            explanation=i.explanation,
            action_taken=i.action_taken,
            is_resolved=i.is_resolved,
            created_at=i.created_at
        )
        for i in insights_db
    ]
    
    return AIInsightListResponse(
        insights=insights,
        total=len(insights)
    )
