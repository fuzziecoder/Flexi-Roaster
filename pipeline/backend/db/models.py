"""
SQLAlchemy Database Models for FlexiRoaster Pipeline Automation.
Complete schema with pipelines, executions, stages, logs, and AI insights.
"""
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text, ForeignKey, 
    JSON, Boolean, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from typing import Optional

Base = declarative_base()


# ===================
# Enums
# ===================

class ExecutionStatus(str, Enum):
    """Execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class StageType(str, Enum):
    """Stage type enumeration"""
    INPUT = "input"
    TRANSFORM = "transform"
    VALIDATION = "validation"
    OUTPUT = "output"


class LogLevel(str, Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class InsightType(str, Enum):
    """AI insight type enumeration"""
    PREDICTION = "prediction"
    ANOMALY = "anomaly"
    OPTIMIZATION = "optimization"
    PERFORMANCE = "performance"
    SUCCESS = "success"


class InsightSeverity(str, Enum):
    """Insight severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SafeActionType(str, Enum):
    """Safe action types for AI recommendations"""
    RETRY_STAGE = "retry_stage"
    SKIP_STAGE = "skip_stage"
    PAUSE_PIPELINE = "pause_pipeline"
    ROLLBACK = "rollback"
    TERMINATE = "terminate"


# ===================
# Models
# ===================

class PipelineDB(Base):
    """Pipeline definition model"""
    __tablename__ = "pipelines"
    
    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    version = Column(String(32), default="1.0.0")
    
    # Pipeline definition (stages, variables, etc.)
    definition = Column(JSON, nullable=False, default=dict)
    
    # Configuration
    config = Column(JSON, default=dict)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    schedule = Column(String(128), nullable=True)  # Cron expression
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    stages = relationship(
        "PipelineStageDB",
        back_populates="pipeline",
        cascade="all, delete-orphan",
        order_by="PipelineStageDB.order"
    )
    executions = relationship(
        "ExecutionDB",
        back_populates="pipeline",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Pipeline(id={self.id}, name={self.name})>"


class PipelineStageDB(Base):
    """Pipeline stage definition model"""
    __tablename__ = "pipeline_stages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    stage_id = Column(String(64), nullable=False, index=True)
    pipeline_id = Column(String(64), ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=False)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    stage_type = Column(String(32), nullable=False)
    
    # Stage configuration
    config = Column(JSON, default=dict)
    
    # Dependencies (list of stage_ids)
    dependencies = Column(JSON, default=list)
    
    # Execution settings
    timeout = Column(Integer, default=120)  # seconds
    max_retries = Column(Integer, default=3)
    retry_delay = Column(Float, default=1.0)
    is_critical = Column(Boolean, default=True)  # If False, can be skipped on failure
    
    # Order in pipeline
    order = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    pipeline = relationship("PipelineDB", back_populates="stages")
    
    __table_args__ = (
        Index("ix_pipeline_stages_pipeline_order", "pipeline_id", "order"),
    )
    
    def __repr__(self):
        return f"<PipelineStage(id={self.stage_id}, name={self.name})>"


class ExecutionDB(Base):
    """Pipeline execution model"""
    __tablename__ = "executions"
    
    id = Column(String(64), primary_key=True, index=True)
    pipeline_id = Column(String(64), ForeignKey("pipelines.id", ondelete="SET NULL"), nullable=True)
    pipeline_name = Column(String(255), nullable=False)
    pipeline_version = Column(String(32), nullable=True)
    
    # Status
    status = Column(String(32), nullable=False, default=ExecutionStatus.PENDING.value, index=True)
    
    # Progress tracking
    total_stages = Column(Integer, default=0)
    completed_stages = Column(Integer, default=0)
    current_stage = Column(String(64), nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=False, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)  # seconds
    
    # Execution context and results
    context = Column(JSON, default=dict)
    variables = Column(JSON, default=dict)
    error = Column(Text, nullable=True)
    
    # AI Safety
    risk_score = Column(Float, nullable=True)
    ai_blocked = Column(Boolean, default=False)
    
    # Trigger information
    triggered_by = Column(String(128), default="manual")  # manual, airflow, schedule, api
    trigger_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    pipeline = relationship("PipelineDB", back_populates="executions")
    stage_executions = relationship(
        "StageExecutionDB",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="StageExecutionDB.started_at"
    )
    logs = relationship(
        "LogDB",
        back_populates="execution",
        cascade="all, delete-orphan",
        order_by="LogDB.timestamp"
    )
    insights = relationship(
        "AIInsightDB",
        back_populates="execution",
        cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index("ix_executions_pipeline_status", "pipeline_id", "status"),
        Index("ix_executions_started_at", "started_at"),
    )
    
    @property
    def progress_percentage(self) -> float:
        if self.total_stages == 0:
            return 0.0
        return (self.completed_stages / self.total_stages) * 100
    
    def __repr__(self):
        return f"<Execution(id={self.id}, status={self.status})>"


class StageExecutionDB(Base):
    """Individual stage execution model"""
    __tablename__ = "stage_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(64), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    stage_id = Column(String(64), nullable=False, index=True)
    stage_name = Column(String(255), nullable=False)
    
    # Status
    status = Column(String(32), nullable=False, default="pending")
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    
    # Retry tracking
    retry_count = Column(Integer, default=0)
    
    # Results
    output = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # AI anomaly detection
    is_anomaly = Column(Boolean, default=False)
    anomaly_reason = Column(Text, nullable=True)
    
    # Relationships
    execution = relationship("ExecutionDB", back_populates="stage_executions")
    
    __table_args__ = (
        Index("ix_stage_executions_execution_stage", "execution_id", "stage_id"),
    )
    
    def __repr__(self):
        return f"<StageExecution(stage={self.stage_id}, status={self.status})>"


class LogDB(Base):
    """Execution log entries"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(64), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    stage_id = Column(String(64), nullable=True)  # NULL for pipeline-level logs
    
    level = Column(String(16), default="info")
    message = Column(Text, nullable=False)
    metadata = Column(JSON, default=dict)  # Additional log data
    
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    execution = relationship("ExecutionDB", back_populates="logs")
    
    __table_args__ = (
        Index("ix_logs_execution_timestamp", "execution_id", "timestamp"),
    )
    
    def __repr__(self):
        return f"<Log(level={self.level}, message={self.message[:50]})>"


class AIInsightDB(Base):
    """AI-generated insights and predictions"""
    __tablename__ = "ai_insights"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Optional links
    pipeline_id = Column(String(64), ForeignKey("pipelines.id", ondelete="CASCADE"), nullable=True)
    execution_id = Column(String(64), ForeignKey("executions.id", ondelete="CASCADE"), nullable=True)
    stage_id = Column(String(64), nullable=True)
    
    # Insight details
    insight_type = Column(String(32), nullable=False)  # prediction, anomaly, optimization
    severity = Column(String(16), nullable=False)  # low, medium, high, critical
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=True)
    
    # AI metrics
    confidence = Column(Float, default=0.0)
    risk_score = Column(Float, nullable=True)
    
    # Explainability
    factors = Column(JSON, default=list)  # List of factors that led to this insight
    explanation = Column(Text, nullable=True)
    
    # Action taken (if any)
    action_taken = Column(String(64), nullable=True)
    action_result = Column(Text, nullable=True)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    execution = relationship("ExecutionDB", back_populates="insights")
    
    __table_args__ = (
        Index("ix_ai_insights_pipeline", "pipeline_id"),
        Index("ix_ai_insights_type_severity", "insight_type", "severity"),
    )
    
    def __repr__(self):
        return f"<AIInsight(type={self.insight_type}, severity={self.severity})>"


class ExecutionLockDB(Base):
    """
    Fallback execution locks for when Redis is unavailable.
    Used to prevent duplicate executions.
    """
    __tablename__ = "execution_locks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    pipeline_id = Column(String(64), nullable=False, unique=True, index=True)
    execution_id = Column(String(64), nullable=True)
    
    locked_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    # Lock holder information
    holder = Column(String(255), nullable=True)  # hostname or worker ID
    
    __table_args__ = (
        Index("ix_execution_locks_expires", "expires_at"),
    )
    
    def __repr__(self):
        return f"<ExecutionLock(pipeline={self.pipeline_id})>"


class MetricDB(Base):
    """System and execution metrics"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    metric_type = Column(String(64), nullable=False, index=True)
    metric_name = Column(String(128), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(32), default="")
    
    # Optional links
    pipeline_id = Column(String(64), nullable=True)
    execution_id = Column(String(64), nullable=True)
    
    # Additional data
    tags = Column(JSON, default=dict)
    
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    __table_args__ = (
        Index("ix_metrics_type_timestamp", "metric_type", "timestamp"),
    )
    
    def __repr__(self):
        return f"<Metric(type={self.metric_type}, value={self.value})>"
