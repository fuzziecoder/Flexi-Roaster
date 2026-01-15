"""
Execution API Routes for FlexiRoaster.
Handles pipeline execution and monitoring.
"""
import logging
from fastapi import APIRouter, HTTPException, status, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from api.schemas import (
    ExecutionCreate, ExecutionResponse, ExecutionDetailResponse,
    ExecutionListResponse, ExecutionStartResponse, ExecutionStopResponse,
    StageExecutionResponse, LogListResponse, LogResponse
)
from db import (
    get_db_session, ExecutionCRUD, StageExecutionCRUD, LogCRUD,
    PipelineCRUD, ExecutionDB, ExecutionStatus
)
from core.executor import pipeline_executor
from core.redis_state import redis_state_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/executions", tags=["executions"])


def _execution_to_response(execution: ExecutionDB) -> ExecutionResponse:
    """Convert database model to response schema"""
    progress = 0.0
    if execution.total_stages > 0:
        progress = (execution.completed_stages / execution.total_stages) * 100
    
    return ExecutionResponse(
        id=execution.id,
        pipeline_id=execution.pipeline_id,
        pipeline_name=execution.pipeline_name,
        status=execution.status,
        total_stages=execution.total_stages,
        completed_stages=execution.completed_stages,
        progress=round(progress, 1),
        risk_score=execution.risk_score,
        triggered_by=execution.triggered_by,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        duration=execution.duration,
        error=execution.error
    )


def _execution_to_detail_response(execution: ExecutionDB) -> ExecutionDetailResponse:
    """Convert database model to detailed response schema"""
    progress = 0.0
    if execution.total_stages > 0:
        progress = (execution.completed_stages / execution.total_stages) * 100
    
    stage_executions = [
        StageExecutionResponse(
            stage_id=se.stage_id,
            stage_name=se.stage_name,
            status=se.status,
            started_at=se.started_at,
            completed_at=se.completed_at,
            duration=se.duration,
            retry_count=se.retry_count,
            output=se.output,
            error=se.error,
            is_anomaly=se.is_anomaly
        )
        for se in (execution.stage_executions or [])
    ]
    
    return ExecutionDetailResponse(
        id=execution.id,
        pipeline_id=execution.pipeline_id,
        pipeline_name=execution.pipeline_name,
        status=execution.status,
        total_stages=execution.total_stages,
        completed_stages=execution.completed_stages,
        progress=round(progress, 1),
        risk_score=execution.risk_score,
        triggered_by=execution.triggered_by,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        duration=execution.duration,
        error=execution.error,
        stage_executions=stage_executions,
        current_stage=execution.current_stage,
        variables=execution.variables or {}
    )


async def execute_pipeline_background(
    pipeline_id: str,
    pipeline_name: str,
    stages: list,
    variables: dict,
    triggered_by: str
):
    """Background task to execute pipeline"""
    try:
        await pipeline_executor.execute_pipeline(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            stages=stages,
            variables=variables,
            triggered_by=triggered_by
        )
    except Exception as e:
        logger.error(f"Background execution failed: {e}")


@router.post(
    "",
    response_model=ExecutionStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start pipeline execution"
)
async def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """
    Start a new pipeline execution.
    
    - **pipeline_id**: ID of the pipeline to execute
    - **variables**: Optional execution variables
    - **triggered_by**: Source of trigger (api, airflow, schedule)
    
    Returns immediately and runs pipeline in background.
    """
    # Get pipeline
    pipeline = PipelineCRUD.get_by_id(db, execution_data.pipeline_id)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {execution_data.pipeline_id}"
        )
    
    if not pipeline.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline is not active: {execution_data.pipeline_id}"
        )
    
    # Prepare stages
    stages = [
        {
            "id": s.stage_id,
            "name": s.name,
            "type": s.stage_type,
            "config": s.config or {},
            "dependencies": s.dependencies or [],
            "timeout": s.timeout,
            "max_retries": s.max_retries,
            "retry_delay": s.retry_delay,
            "is_critical": s.is_critical
        }
        for s in pipeline.stages
    ]
    
    # Start execution in background
    background_tasks.add_task(
        execute_pipeline_background,
        pipeline.id,
        pipeline.name,
        stages,
        execution_data.variables,
        execution_data.triggered_by
    )
    
    return ExecutionStartResponse(
        success=True,
        status="accepted",
        message=f"Pipeline execution started for {pipeline.name}"
    )


@router.post(
    "/{pipeline_id}/execute",
    response_model=ExecutionStartResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Execute a specific pipeline"
)
async def execute_pipeline(
    pipeline_id: str,
    background_tasks: BackgroundTasks,
    variables: dict = None,
    triggered_by: str = "api",
    db: Session = Depends(get_db_session)
):
    """
    Execute a specific pipeline by ID.
    This is the endpoint called by Airflow DAGs.
    
    - **pipeline_id**: Unique pipeline identifier
    - **variables**: Optional execution variables
    - **triggered_by**: Source of trigger
    """
    # Get pipeline
    pipeline = PipelineCRUD.get_by_id(db, pipeline_id)
    if not pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {pipeline_id}"
        )
    
    if not pipeline.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline is not active: {pipeline_id}"
        )
    
    # Prepare stages
    stages = [
        {
            "id": s.stage_id,
            "name": s.name,
            "type": s.stage_type,
            "config": s.config or {},
            "dependencies": s.dependencies or [],
            "timeout": s.timeout,
            "max_retries": s.max_retries,
            "retry_delay": s.retry_delay,
            "is_critical": s.is_critical
        }
        for s in pipeline.stages
    ]
    
    # Start execution in background
    background_tasks.add_task(
        execute_pipeline_background,
        pipeline.id,
        pipeline.name,
        stages,
        variables or {},
        triggered_by
    )
    
    return ExecutionStartResponse(
        success=True,
        status="accepted",
        message=f"Pipeline execution started for {pipeline.name}"
    )


@router.get(
    "",
    response_model=ExecutionListResponse,
    summary="List all executions"
)
async def list_executions(
    pipeline_id: Optional[str] = None,
    status: Optional[str] = None,
    hours: int = 24,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    Get a list of executions.
    
    - **pipeline_id**: Filter by pipeline ID
    - **status**: Filter by status
    - **hours**: Get executions from last N hours
    - **skip**: Number to skip (pagination)
    - **limit**: Maximum to return
    """
    if pipeline_id:
        executions = ExecutionCRUD.get_by_pipeline(
            db, pipeline_id, status=status, skip=skip, limit=limit
        )
    else:
        executions = ExecutionCRUD.get_recent(
            db, hours=hours, status=status, limit=limit
        )
    
    return ExecutionListResponse(
        executions=[_execution_to_response(e) for e in executions],
        total=len(executions)
    )


@router.get(
    "/{execution_id}",
    response_model=ExecutionDetailResponse,
    summary="Get execution details"
)
async def get_execution(
    execution_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Get detailed information about a specific execution.
    
    - **execution_id**: Unique execution identifier
    """
    # Check Redis for real-time state first
    redis_state = await redis_state_manager.get_execution_state(execution_id)
    
    # Get from database
    execution = ExecutionCRUD.get_by_id(db, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    response = _execution_to_detail_response(execution)
    
    # Merge real-time state if available
    if redis_state:
        response.status = redis_state.get("state", response.status)
    
    return response


@router.post(
    "/{execution_id}/stop",
    response_model=ExecutionStopResponse,
    summary="Stop a running execution"
)
async def stop_execution(
    execution_id: str,
    db: Session = Depends(get_db_session)
):
    """
    Stop a running execution.
    
    - **execution_id**: Unique execution identifier
    """
    execution = ExecutionCRUD.get_by_id(db, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    if execution.status not in [ExecutionStatus.PENDING.value, ExecutionStatus.RUNNING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot stop execution with status: {execution.status}"
        )
    
    # Try to stop via executor
    stopped = await pipeline_executor.stop_execution(execution_id)
    
    if not stopped:
        # Update database directly if not in active executions
        ExecutionCRUD.update_status(
            db, execution_id, ExecutionStatus.CANCELLED
        )
        db.commit()
    
    return ExecutionStopResponse(
        success=True,
        message=f"Execution {execution_id} stop requested"
    )


@router.post(
    "/{execution_id}/pause",
    response_model=ExecutionStopResponse,
    summary="Pause a running execution"
)
async def pause_execution(
    execution_id: str,
    db: Session = Depends(get_db_session)
):
    """Pause a running execution"""
    execution = ExecutionCRUD.get_by_id(db, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    if execution.status != ExecutionStatus.RUNNING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot pause execution with status: {execution.status}"
        )
    
    paused = await pipeline_executor.pause_execution(execution_id)
    
    return ExecutionStopResponse(
        success=paused,
        message=f"Execution {execution_id} {'paused' if paused else 'pause failed'}"
    )


@router.post(
    "/{execution_id}/resume",
    response_model=ExecutionStopResponse,
    summary="Resume a paused execution"
)
async def resume_execution(
    execution_id: str,
    db: Session = Depends(get_db_session)
):
    """Resume a paused execution"""
    execution = ExecutionCRUD.get_by_id(db, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    if execution.status != ExecutionStatus.PAUSED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot resume execution with status: {execution.status}"
        )
    
    resumed = await pipeline_executor.resume_execution(execution_id)
    
    return ExecutionStopResponse(
        success=resumed,
        message=f"Execution {execution_id} {'resumed' if resumed else 'resume failed'}"
    )


@router.get(
    "/{execution_id}/logs",
    response_model=LogListResponse,
    summary="Get execution logs"
)
async def get_execution_logs(
    execution_id: str,
    level: Optional[str] = None,
    limit: int = 500,
    db: Session = Depends(get_db_session)
):
    """
    Get logs for a specific execution.
    
    - **execution_id**: Unique execution identifier
    - **level**: Filter by log level
    - **limit**: Maximum logs to return
    """
    execution = ExecutionCRUD.get_by_id(db, execution_id)
    if not execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    logs = LogCRUD.get_by_execution(db, execution_id, level=level, limit=limit)
    
    return LogListResponse(
        logs=[
            LogResponse(
                id=log.id,
                level=log.level,
                message=log.message,
                stage_id=log.stage_id,
                timestamp=log.timestamp,
                metadata=log.metadata or {}
            )
            for log in logs
        ],
        total=len(logs)
    )


@router.get(
    "/running",
    response_model=ExecutionListResponse,
    summary="Get all running executions"
)
async def get_running_executions(
    db: Session = Depends(get_db_session)
):
    """Get all currently running executions"""
    executions = ExecutionCRUD.get_running(db)
    
    return ExecutionListResponse(
        executions=[_execution_to_response(e) for e in executions],
        total=len(executions)
    )
