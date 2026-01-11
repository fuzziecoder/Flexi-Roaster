"""
CRUD Operations for Database
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from backend.db.models import PipelineDB, ExecutionDB, StageExecutionDB, LogDB, MetricDB
from backend.models.pipeline import PipelineDefinition, PipelineExecution, StageExecution


# Pipeline CRUD
def create_pipeline(db: Session, pipeline: PipelineDefinition) -> PipelineDB:
    """Create a new pipeline in database"""
    db_pipeline = PipelineDB(
        id=pipeline.id,
        name=pipeline.name,
        description=pipeline.description,
        version=pipeline.version,
        definition={
            "stages": [stage.model_dump() for stage in pipeline.stages],
            "variables": pipeline.variables
        }
    )
    db.add(db_pipeline)
    db.commit()
    db.refresh(db_pipeline)
    return db_pipeline


def get_pipeline(db: Session, pipeline_id: str) -> Optional[PipelineDB]:
    """Get pipeline by ID"""
    return db.query(PipelineDB).filter(PipelineDB.id == pipeline_id).first()


def get_pipelines(db: Session, skip: int = 0, limit: int = 100) -> List[PipelineDB]:
    """Get all pipelines"""
    return db.query(PipelineDB).offset(skip).limit(limit).all()


def update_pipeline(db: Session, pipeline_id: str, pipeline: PipelineDefinition) -> Optional[PipelineDB]:
    """Update a pipeline"""
    db_pipeline = get_pipeline(db, pipeline_id)
    if db_pipeline:
        db_pipeline.name = pipeline.name
        db_pipeline.description = pipeline.description
        db_pipeline.version = pipeline.version
        db_pipeline.definition = {
            "stages": [stage.model_dump() for stage in pipeline.stages],
            "variables": pipeline.variables
        }
        db_pipeline.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_pipeline)
    return db_pipeline


def delete_pipeline(db: Session, pipeline_id: str) -> bool:
    """Delete a pipeline"""
    db_pipeline = get_pipeline(db, pipeline_id)
    if db_pipeline:
        db.delete(db_pipeline)
        db.commit()
        return True
    return False


# Execution CRUD
def create_execution(db: Session, execution: PipelineExecution) -> ExecutionDB:
    """Create a new execution in database"""
    db_execution = ExecutionDB(
        id=execution.id,
        pipeline_id=execution.pipeline_id,
        pipeline_name=execution.pipeline_name,
        status=execution.status,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        duration=execution.duration,
        context=execution.context,
        error=execution.error
    )
    db.add(db_execution)
    db.commit()
    db.refresh(db_execution)
    return db_execution


def get_execution(db: Session, execution_id: str) -> Optional[ExecutionDB]:
    """Get execution by ID"""
    return db.query(ExecutionDB).filter(ExecutionDB.id == execution_id).first()


def get_executions(db: Session, skip: int = 0, limit: int = 50) -> List[ExecutionDB]:
    """Get all executions"""
    return db.query(ExecutionDB).order_by(ExecutionDB.started_at.desc()).offset(skip).limit(limit).all()


def update_execution(db: Session, execution: PipelineExecution) -> Optional[ExecutionDB]:
    """Update an execution"""
    db_execution = get_execution(db, execution.id)
    if db_execution:
        db_execution.status = execution.status
        db_execution.completed_at = execution.completed_at
        db_execution.duration = execution.duration
        db_execution.context = execution.context
        db_execution.error = execution.error
        db.commit()
        db.refresh(db_execution)
    return db_execution


# Stage Execution CRUD
def create_stage_execution(db: Session, execution_id: str, stage_exec: StageExecution) -> StageExecutionDB:
    """Create a stage execution"""
    db_stage = StageExecutionDB(
        execution_id=execution_id,
        stage_id=stage_exec.stage_id,
        status=stage_exec.status,
        started_at=stage_exec.started_at,
        completed_at=stage_exec.completed_at,
        duration=stage_exec.duration,
        output=stage_exec.output,
        error=stage_exec.error
    )
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


# Log CRUD
def create_log(db: Session, execution_id: str, level: str, message: str) -> LogDB:
    """Create a log entry"""
    db_log = LogDB(
        execution_id=execution_id,
        level=level,
        message=message
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_execution_logs(db: Session, execution_id: str) -> List[LogDB]:
    """Get all logs for an execution"""
    return db.query(LogDB).filter(LogDB.execution_id == execution_id).order_by(LogDB.timestamp).all()


# Metrics CRUD
def create_metric(db: Session, metric_type: str, value: float, unit: str = "", metric_metadata: dict = None) -> MetricDB:
    """Create a metric entry"""
    db_metric = MetricDB(
        metric_type=metric_type,
        value=value,
        unit=unit,
        metric_metadata=metric_metadata or {}
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


def get_metrics_history(db: Session, hours: int = 24) -> List[MetricDB]:
    """Get metrics from last N hours"""
    start_time = datetime.utcnow() - timedelta(hours=hours)
    return db.query(MetricDB).filter(MetricDB.timestamp >= start_time).order_by(MetricDB.timestamp).all()


def get_latest_metrics(db: Session) -> List[MetricDB]:
    """Get latest metrics (one per type)"""
    # Get distinct metric types
    metric_types = db.query(MetricDB.metric_type).distinct().all()
    
    latest_metrics = []
    for (metric_type,) in metric_types:
        latest = db.query(MetricDB).filter(
            MetricDB.metric_type == metric_type
        ).order_by(MetricDB.timestamp.desc()).first()
        if latest:
            latest_metrics.append(latest)
    
    return latest_metrics
