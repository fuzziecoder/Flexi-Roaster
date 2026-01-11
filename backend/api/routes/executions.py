"""
Updated Execution API Routes with Database Integration
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from backend.api.schemas import (
    ExecutionCreate,
    ExecutionResponse,
    ExecutionLogsResponse,
    StageExecutionResponse
)
from backend.core.pipeline_engine import PipelineEngine
from backend.core.executor import PipelineExecutor
from backend.db.database import get_db
from backend.db import crud

router = APIRouter(prefix="/api/executions", tags=["executions"])

# Global instances
engine = PipelineEngine()
executor = PipelineExecutor()


def run_pipeline_execution(execution_id: str):
    """Background task to run pipeline execution"""
    from backend.db.database import SessionLocal
    db = SessionLocal()
    
    try:
        db_execution = crud.get_execution(db, execution_id)
        if not db_execution:
            return
        
        # Load pipeline into engine if not already loaded
        db_pipeline = crud.get_pipeline(db, db_execution.pipeline_id)
        if not db_pipeline:
            return
        
        if db_execution.pipeline_id not in engine.pipelines:
            data = {
                "id": db_pipeline.id,
                "name": db_pipeline.name,
                "description": db_pipeline.description,
                "version": db_pipeline.version,
                "stages": db_pipeline.definition.get("stages", []),
                "variables": db_pipeline.definition.get("variables", {})
            }
            pipeline = engine.load_from_dict(data)
        else:
            pipeline = engine.get_pipeline(db_execution.pipeline_id)
        
        # Create execution object
        execution = engine.create_execution(db_execution.pipeline_id)
        execution.id = db_execution.id
        execution.context = db_execution.context
        
        # Execute pipeline
        result = executor.execute(pipeline, execution)
        
        # Update database
        crud.update_execution(db, result)
        
        # Save stage executions
        for stage_exec in result.stage_executions:
            crud.create_stage_execution(db, result.id, stage_exec)
        
        # Save logs
        for log in result.context.get('logs', []):
            crud.create_log(db, result.id, "info", log)
            
    finally:
        db.close()


@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start a new pipeline execution"""
    # Check if pipeline exists
    db_pipeline = crud.get_pipeline(db, execution_data.pipeline_id)
    if not db_pipeline:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {execution_data.pipeline_id}"
        )
    
    # Load pipeline into engine
    if execution_data.pipeline_id not in engine.pipelines:
        data = {
            "id": db_pipeline.id,
            "name": db_pipeline.name,
            "description": db_pipeline.description,
            "version": db_pipeline.version,
            "stages": db_pipeline.definition.get("stages", []),
            "variables": db_pipeline.definition.get("variables", {})
        }
        engine.load_from_dict(data)
    
    # Create execution
    execution = engine.create_execution(execution_data.pipeline_id)
    
    # Merge custom variables
    if execution_data.variables:
        execution.context.update(execution_data.variables)
    
    # Save to database
    db_execution = crud.create_execution(db, execution)
    
    # Run in background
    background_tasks.add_task(run_pipeline_execution, execution.id)
    
    return ExecutionResponse(
        id=db_execution.id,
        pipeline_id=db_execution.pipeline_id,
        pipeline_name=db_execution.pipeline_name,
        status=db_execution.status,
        started_at=db_execution.started_at,
        completed_at=db_execution.completed_at,
        duration=db_execution.duration,
        stage_executions=[],
        error=db_execution.error
    )


@router.get("", response_model=List[ExecutionResponse])
async def list_executions(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """List all executions"""
    db_executions = crud.get_executions(db, skip=skip, limit=limit)
    
    return [
        ExecutionResponse(
            id=e.id,
            pipeline_id=e.pipeline_id,
            pipeline_name=e.pipeline_name,
            status=e.status,
            started_at=e.started_at,
            completed_at=e.completed_at,
            duration=e.duration,
            stage_executions=[
                StageExecutionResponse(
                    stage_id=se.stage_id,
                    status=se.status,
                    started_at=se.started_at,
                    completed_at=se.completed_at,
                    duration=se.duration,
                    output=se.output,
                    error=se.error
                )
                for se in e.stage_executions
            ],
            error=e.error
        )
        for e in db_executions
    ]


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(execution_id: str, db: Session = Depends(get_db)):
    """Get execution status and details"""
    db_execution = crud.get_execution(db, execution_id)
    
    if not db_execution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )
    
    return ExecutionResponse(
        id=db_execution.id,
        pipeline_id=db_execution.pipeline_id,
        pipeline_name=db_execution.pipeline_name,
        status=db_execution.status,
        started_at=db_execution.started_at,
        completed_at=db_execution.completed_at,
        duration=db_execution.duration,
        stage_executions=[
            StageExecutionResponse(
                stage_id=se.stage_id,
                status=se.status,
                started_at=se.started_at,
                completed_at=se.completed_at,
                duration=se.duration,
                output=se.output,
                error=se.error
            )
            for se in db_execution.stage_executions
        ],
        error=db_execution.error
    )


@router.get("/{execution_id}/logs", response_model=ExecutionLogsResponse)
async def get_execution_logs(execution_id: str, db: Session = Depends(get_db)):
    """Get execution logs"""
    db_logs = crud.get_execution_logs(db, execution_id)
    
    logs = [f"[{log.timestamp.isoformat()}] [{log.level.upper()}] {log.message}" for log in db_logs]
    
    return ExecutionLogsResponse(
        execution_id=execution_id,
        logs=logs
    )
