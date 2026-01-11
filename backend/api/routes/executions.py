"""
Execution management API routes.
Handles pipeline execution and execution monitoring.
"""
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from typing import Dict
import uuid

from backend.api.schemas import (
    ExecutionCreate,
    ExecutionResponse,
    ExecutionDetailResponse,
    ExecutionListResponse,
    SuccessResponse
)
from backend.models.pipeline import Execution, ExecutionStatus
from backend.core.executor import PipelineExecutor

router = APIRouter(prefix="/executions", tags=["executions"])

# In-memory storage (will be replaced with database in Phase 3)
executions_db: Dict[str, Execution] = {}

# Import pipelines_db from pipelines route
from backend.api.routes.pipelines import pipelines_db


async def execute_pipeline_background(pipeline_id: str, execution_id: str):
    """Background task to execute pipeline"""
    try:
        pipeline = pipelines_db[pipeline_id]
        executor = PipelineExecutor()
        execution = executor.execute(pipeline)
        execution.id = execution_id  # Use the pre-assigned ID
        executions_db[execution_id] = execution
    except Exception as e:
        # Update execution with error
        if execution_id in executions_db:
            executions_db[execution_id].status = ExecutionStatus.FAILED
            executions_db[execution_id].error = str(e)


@router.post(
    "",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start pipeline execution"
)
async def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks
):
    """
    Start a new pipeline execution.
    
    - **pipeline_id**: ID of the pipeline to execute
    
    Returns execution ID immediately and runs pipeline in background.
    """
    if execution_data.pipeline_id not in pipelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {execution_data.pipeline_id}"
        )
    
    # Create execution record
    execution_id = f"exec-{uuid.uuid4()}"
    pipeline = pipelines_db[execution_data.pipeline_id]
    
    from datetime import datetime
    execution = Execution(
        id=execution_id,
        pipeline_id=execution_data.pipeline_id,
        status=ExecutionStatus.PENDING,
        started_at=datetime.now(),
        total_stages=len(pipeline.stages)
    )
    
    executions_db[execution_id] = execution
    
    # Start execution in background
    background_tasks.add_task(
        execute_pipeline_background,
        execution_data.pipeline_id,
        execution_id
    )
    
    return execution


@router.get(
    "",
    response_model=ExecutionListResponse,
    summary="List all executions"
)
async def list_executions(
    pipeline_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Get a list of all executions.
    
    - **pipeline_id**: Filter by pipeline ID (optional)
    - **status**: Filter by status (optional)
    - **skip**: Number of executions to skip (pagination)
    - **limit**: Maximum number of executions to return
    """
    all_executions = list(executions_db.values())
    
    # Apply filters
    if pipeline_id:
        all_executions = [e for e in all_executions if e.pipeline_id == pipeline_id]
    if status:
        all_executions = [e for e in all_executions if e.status.value == status]
    
    # Sort by started_at descending
    all_executions.sort(key=lambda x: x.started_at, reverse=True)
    
    total = len(all_executions)
    executions = all_executions[skip : skip + limit]
    
    return ExecutionListResponse(
        executions=executions,
        total=total
    )


@router.get(
    "/{execution_id}",
    response_model=ExecutionDetailResponse,
    summary="Get execution details"
)
async def get_execution(execution_id: str):
    """
    Get details of a specific execution including logs.
    
    - **execution_id**: Unique execution identifier
    """
    if execution_id not in executions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    return executions_db[execution_id]


@router.get(
    "/{execution_id}/logs",
    response_model=List,
    summary="Get execution logs"
)
async def get_execution_logs(execution_id: str):
    """
    Get logs for a specific execution.
    
    - **execution_id**: Unique execution identifier
    """
    if execution_id not in executions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    execution = executions_db[execution_id]
    return execution.logs


@router.delete(
    "/{execution_id}",
    response_model=SuccessResponse,
    summary="Cancel execution"
)
async def cancel_execution(execution_id: str):
    """
    Cancel a running execution.
    
    - **execution_id**: Unique execution identifier
    """
    if execution_id not in executions_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    execution = executions_db[execution_id]
    
    if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel execution with status: {execution.status.value}"
        )
    
    execution.status = ExecutionStatus.CANCELLED
    from datetime import datetime
    execution.completed_at = datetime.now()
    
    return SuccessResponse(
        message=f"Execution {execution_id} cancelled successfully"
    )
