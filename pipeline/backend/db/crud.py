"""
Database CRUD Operations for FlexiRoaster.
Provides type-safe database operations for all models.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import logging

from db.models import (
    PipelineDB, PipelineStageDB, ExecutionDB, StageExecutionDB,
    LogDB, AIInsightDB, ExecutionLockDB, MetricDB,
    ExecutionStatus
)

logger = logging.getLogger(__name__)


# ===================
# Pipeline CRUD
# ===================

class PipelineCRUD:
    """CRUD operations for Pipelines"""
    
    @staticmethod
    def create(
        db: Session,
        id: str,
        name: str,
        definition: Dict[str, Any],
        description: Optional[str] = None,
        version: str = "1.0.0",
        config: Optional[Dict] = None,
        schedule: Optional[str] = None
    ) -> PipelineDB:
        """Create a new pipeline"""
        pipeline = PipelineDB(
            id=id,
            name=name,
            description=description,
            version=version,
            definition=definition,
            config=config or {},
            schedule=schedule
        )
        db.add(pipeline)
        db.flush()
        return pipeline
    
    @staticmethod
    def get_by_id(db: Session, pipeline_id: str) -> Optional[PipelineDB]:
        """Get pipeline by ID"""
        return db.query(PipelineDB).filter(PipelineDB.id == pipeline_id).first()
    
    @staticmethod
    def get_all(
        db: Session,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PipelineDB]:
        """Get all pipelines with optional filtering"""
        query = db.query(PipelineDB)
        if is_active is not None:
            query = query.filter(PipelineDB.is_active == is_active)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update(
        db: Session,
        pipeline_id: str,
        **kwargs
    ) -> Optional[PipelineDB]:
        """Update pipeline fields"""
        pipeline = PipelineCRUD.get_by_id(db, pipeline_id)
        if pipeline:
            for key, value in kwargs.items():
                if hasattr(pipeline, key):
                    setattr(pipeline, key, value)
            db.flush()
        return pipeline
    
    @staticmethod
    def delete(db: Session, pipeline_id: str) -> bool:
        """Delete a pipeline"""
        pipeline = PipelineCRUD.get_by_id(db, pipeline_id)
        if pipeline:
            db.delete(pipeline)
            db.flush()
            return True
        return False
    
    @staticmethod
    def count(db: Session, is_active: Optional[bool] = None) -> int:
        """Count pipelines"""
        query = db.query(func.count(PipelineDB.id))
        if is_active is not None:
            query = query.filter(PipelineDB.is_active == is_active)
        return query.scalar()


# ===================
# Execution CRUD
# ===================

class ExecutionCRUD:
    """CRUD operations for Executions"""
    
    @staticmethod
    def create(
        db: Session,
        id: str,
        pipeline_id: str,
        pipeline_name: str,
        total_stages: int,
        triggered_by: str = "manual",
        variables: Optional[Dict] = None,
        trigger_metadata: Optional[Dict] = None,
        risk_score: Optional[float] = None
    ) -> ExecutionDB:
        """Create a new execution"""
        execution = ExecutionDB(
            id=id,
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            total_stages=total_stages,
            triggered_by=triggered_by,
            variables=variables or {},
            trigger_metadata=trigger_metadata or {},
            risk_score=risk_score
        )
        db.add(execution)
        db.flush()
        return execution
    
    @staticmethod
    def get_by_id(db: Session, execution_id: str) -> Optional[ExecutionDB]:
        """Get execution by ID"""
        return db.query(ExecutionDB).filter(ExecutionDB.id == execution_id).first()
    
    @staticmethod
    def get_by_pipeline(
        db: Session,
        pipeline_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ExecutionDB]:
        """Get executions for a pipeline"""
        query = db.query(ExecutionDB).filter(ExecutionDB.pipeline_id == pipeline_id)
        if status:
            query = query.filter(ExecutionDB.status == status)
        return query.order_by(desc(ExecutionDB.started_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_recent(
        db: Session,
        hours: int = 24,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[ExecutionDB]:
        """Get recent executions"""
        since = datetime.now() - timedelta(hours=hours)
        query = db.query(ExecutionDB).filter(ExecutionDB.started_at >= since)
        if status:
            query = query.filter(ExecutionDB.status == status)
        return query.order_by(desc(ExecutionDB.started_at)).limit(limit).all()
    
    @staticmethod
    def get_running(db: Session) -> List[ExecutionDB]:
        """Get all running executions"""
        return db.query(ExecutionDB).filter(
            ExecutionDB.status == ExecutionStatus.RUNNING.value
        ).all()
    
    @staticmethod
    def update_status(
        db: Session,
        execution_id: str,
        status: ExecutionStatus,
        error: Optional[str] = None,
        completed_stages: Optional[int] = None,
        current_stage: Optional[str] = None
    ) -> Optional[ExecutionDB]:
        """Update execution status"""
        execution = ExecutionCRUD.get_by_id(db, execution_id)
        if execution:
            execution.status = status.value
            if error:
                execution.error = error
            if completed_stages is not None:
                execution.completed_stages = completed_stages
            if current_stage is not None:
                execution.current_stage = current_stage
            
            # Set completion time for terminal states
            if status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED,
                          ExecutionStatus.CANCELLED, ExecutionStatus.ROLLED_BACK]:
                execution.completed_at = datetime.now()
                if execution.started_at:
                    execution.duration = (execution.completed_at - execution.started_at).total_seconds()
            
            db.flush()
        return execution
    
    @staticmethod
    def get_stats(
        db: Session,
        pipeline_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get execution statistics for a pipeline"""
        since = datetime.now() - timedelta(days=days)
        
        executions = db.query(ExecutionDB).filter(
            and_(
                ExecutionDB.pipeline_id == pipeline_id,
                ExecutionDB.started_at >= since
            )
        ).all()
        
        total = len(executions)
        if total == 0:
            return {
                "total": 0,
                "completed": 0,
                "failed": 0,
                "avg_duration": 0,
                "success_rate": 0
            }
        
        completed = sum(1 for e in executions if e.status == ExecutionStatus.COMPLETED.value)
        failed = sum(1 for e in executions if e.status == ExecutionStatus.FAILED.value)
        durations = [e.duration for e in executions if e.duration]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "avg_duration": round(avg_duration, 2),
            "success_rate": round((completed / total) * 100, 2) if total > 0 else 0
        }


# ===================
# Stage Execution CRUD
# ===================

class StageExecutionCRUD:
    """CRUD operations for Stage Executions"""
    
    @staticmethod
    def create(
        db: Session,
        execution_id: str,
        stage_id: str,
        stage_name: str
    ) -> StageExecutionDB:
        """Create a new stage execution record"""
        stage_exec = StageExecutionDB(
            execution_id=execution_id,
            stage_id=stage_id,
            stage_name=stage_name,
            status="pending"
        )
        db.add(stage_exec)
        db.flush()
        return stage_exec
    
    @staticmethod
    def get_by_execution(db: Session, execution_id: str) -> List[StageExecutionDB]:
        """Get all stage executions for an execution"""
        return db.query(StageExecutionDB).filter(
            StageExecutionDB.execution_id == execution_id
        ).order_by(StageExecutionDB.started_at).all()
    
    @staticmethod
    def update(
        db: Session,
        execution_id: str,
        stage_id: str,
        **kwargs
    ) -> Optional[StageExecutionDB]:
        """Update stage execution"""
        stage_exec = db.query(StageExecutionDB).filter(
            and_(
                StageExecutionDB.execution_id == execution_id,
                StageExecutionDB.stage_id == stage_id
            )
        ).first()
        
        if stage_exec:
            for key, value in kwargs.items():
                if hasattr(stage_exec, key):
                    setattr(stage_exec, key, value)
            db.flush()
        return stage_exec


# ===================
# Log CRUD
# ===================

class LogCRUD:
    """CRUD operations for Logs"""
    
    @staticmethod
    def create(
        db: Session,
        execution_id: str,
        level: str,
        message: str,
        stage_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> LogDB:
        """Create a new log entry"""
        log = LogDB(
            execution_id=execution_id,
            stage_id=stage_id,
            level=level,
            message=message,
            metadata=metadata or {}
        )
        db.add(log)
        db.flush()
        return log
    
    @staticmethod
    def get_by_execution(
        db: Session,
        execution_id: str,
        level: Optional[str] = None,
        limit: int = 500
    ) -> List[LogDB]:
        """Get logs for an execution"""
        query = db.query(LogDB).filter(LogDB.execution_id == execution_id)
        if level:
            query = query.filter(LogDB.level == level)
        return query.order_by(LogDB.timestamp).limit(limit).all()
    
    @staticmethod
    def get_recent(db: Session, minutes: int = 60, limit: int = 100) -> List[LogDB]:
        """Get recent logs across all executions"""
        since = datetime.now() - timedelta(minutes=minutes)
        return db.query(LogDB).filter(
            LogDB.timestamp >= since
        ).order_by(desc(LogDB.timestamp)).limit(limit).all()


# ===================
# AI Insight CRUD
# ===================

class AIInsightCRUD:
    """CRUD operations for AI Insights"""
    
    @staticmethod
    def create(
        db: Session,
        insight_type: str,
        severity: str,
        title: str,
        message: str,
        pipeline_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        stage_id: Optional[str] = None,
        recommendation: Optional[str] = None,
        confidence: float = 0.0,
        risk_score: Optional[float] = None,
        factors: Optional[List] = None,
        explanation: Optional[str] = None
    ) -> AIInsightDB:
        """Create a new AI insight"""
        insight = AIInsightDB(
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            stage_id=stage_id,
            insight_type=insight_type,
            severity=severity,
            title=title,
            message=message,
            recommendation=recommendation,
            confidence=confidence,
            risk_score=risk_score,
            factors=factors or [],
            explanation=explanation
        )
        db.add(insight)
        db.flush()
        return insight
    
    @staticmethod
    def get_by_pipeline(
        db: Session,
        pipeline_id: str,
        unresolved_only: bool = False,
        limit: int = 50
    ) -> List[AIInsightDB]:
        """Get insights for a pipeline"""
        query = db.query(AIInsightDB).filter(AIInsightDB.pipeline_id == pipeline_id)
        if unresolved_only:
            query = query.filter(AIInsightDB.is_resolved == False)
        return query.order_by(desc(AIInsightDB.created_at)).limit(limit).all()
    
    @staticmethod
    def get_by_execution(db: Session, execution_id: str) -> List[AIInsightDB]:
        """Get insights for an execution"""
        return db.query(AIInsightDB).filter(
            AIInsightDB.execution_id == execution_id
        ).order_by(AIInsightDB.created_at).all()
    
    @staticmethod
    def get_recent_high_severity(db: Session, hours: int = 24, limit: int = 20) -> List[AIInsightDB]:
        """Get recent high severity insights"""
        since = datetime.now() - timedelta(hours=hours)
        return db.query(AIInsightDB).filter(
            and_(
                AIInsightDB.created_at >= since,
                AIInsightDB.severity.in_(["high", "critical"])
            )
        ).order_by(desc(AIInsightDB.created_at)).limit(limit).all()
    
    @staticmethod
    def mark_resolved(
        db: Session,
        insight_id: int,
        action_taken: Optional[str] = None,
        action_result: Optional[str] = None
    ) -> Optional[AIInsightDB]:
        """Mark an insight as resolved"""
        insight = db.query(AIInsightDB).filter(AIInsightDB.id == insight_id).first()
        if insight:
            insight.is_resolved = True
            insight.resolved_at = datetime.now()
            if action_taken:
                insight.action_taken = action_taken
            if action_result:
                insight.action_result = action_result
            db.flush()
        return insight


# ===================
# Execution Lock CRUD
# ===================

class ExecutionLockCRUD:
    """CRUD operations for Execution Locks (DB fallback)"""
    
    @staticmethod
    def acquire_lock(
        db: Session,
        pipeline_id: str,
        execution_id: str,
        timeout_seconds: int = 3600,
        holder: Optional[str] = None
    ) -> bool:
        """Try to acquire a lock using the database"""
        # Clean up expired locks first
        ExecutionLockCRUD.cleanup_expired(db)
        
        # Check if lock exists
        existing = db.query(ExecutionLockDB).filter(
            ExecutionLockDB.pipeline_id == pipeline_id
        ).first()
        
        if existing:
            return False
        
        # Create new lock
        lock = ExecutionLockDB(
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            expires_at=datetime.now() + timedelta(seconds=timeout_seconds),
            holder=holder
        )
        db.add(lock)
        try:
            db.flush()
            return True
        except Exception:
            return False
    
    @staticmethod
    def release_lock(db: Session, pipeline_id: str) -> bool:
        """Release a lock"""
        lock = db.query(ExecutionLockDB).filter(
            ExecutionLockDB.pipeline_id == pipeline_id
        ).first()
        if lock:
            db.delete(lock)
            db.flush()
            return True
        return False
    
    @staticmethod
    def is_locked(db: Session, pipeline_id: str) -> bool:
        """Check if a pipeline is locked"""
        ExecutionLockCRUD.cleanup_expired(db)
        return db.query(ExecutionLockDB).filter(
            ExecutionLockDB.pipeline_id == pipeline_id
        ).first() is not None
    
    @staticmethod
    def cleanup_expired(db: Session) -> int:
        """Remove expired locks"""
        result = db.query(ExecutionLockDB).filter(
            ExecutionLockDB.expires_at < datetime.now()
        ).delete()
        db.flush()
        return result


# ===================
# Metric CRUD
# ===================

class MetricCRUD:
    """CRUD operations for Metrics"""
    
    @staticmethod
    def record(
        db: Session,
        metric_type: str,
        metric_name: str,
        value: float,
        unit: str = "",
        pipeline_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        tags: Optional[Dict] = None
    ) -> MetricDB:
        """Record a metric"""
        metric = MetricDB(
            metric_type=metric_type,
            metric_name=metric_name,
            value=value,
            unit=unit,
            pipeline_id=pipeline_id,
            execution_id=execution_id,
            tags=tags or {}
        )
        db.add(metric)
        db.flush()
        return metric
    
    @staticmethod
    def get_recent(
        db: Session,
        metric_type: str,
        hours: int = 24,
        limit: int = 1000
    ) -> List[MetricDB]:
        """Get recent metrics by type"""
        since = datetime.now() - timedelta(hours=hours)
        return db.query(MetricDB).filter(
            and_(
                MetricDB.metric_type == metric_type,
                MetricDB.timestamp >= since
            )
        ).order_by(MetricDB.timestamp).limit(limit).all()
