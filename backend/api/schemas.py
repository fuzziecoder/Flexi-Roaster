"""
Pydantic schemas for API request/response models.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class StageTypeSchema(str, Enum):
    """Stage types"""
    INPUT = "input"
    TRANSFORM = "transform"
    OUTPUT = "output"
    VALIDATION = "validation"


class ExecutionStatusSchema(str, Enum):
    """Execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AirflowCallbackTypeSchema(str, Enum):
    """Supported callback event types from Airflow."""
    SUCCESS = "success"
    FAILURE = "failure"
    RETRY = "retry"
    RUNNING = "running"
    CANCELLED = "cancelled"


class LogLevelSchema(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


# Stage Schemas
class StageBase(BaseModel):
    """Base stage schema"""
    name: str
    type: StageTypeSchema
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)


class StageCreate(StageBase):
    """Schema for creating a stage"""
    id: Optional[str] = None


class StageResponse(StageBase):
    """Schema for stage response"""
    id: str
    
    class Config:
        from_attributes = True


# Pipeline Schemas
class PipelineBase(BaseModel):
    """Base pipeline schema"""
    name: str
    description: str


class PipelineCreate(PipelineBase):
    """Schema for creating a pipeline"""
    stages: List[StageCreate]


class PipelineUpdate(BaseModel):
    """Schema for updating a pipeline"""
    name: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[StageCreate]] = None


class PipelineResponse(PipelineBase):
    """Schema for pipeline response"""
    id: str
    stages: List[StageResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PipelineListResponse(BaseModel):
    """Schema for pipeline list response"""
    pipelines: List[PipelineResponse]
    total: int


# Execution Schemas
class ExecutionCreate(BaseModel):
    """Schema for creating an execution"""
    pipeline_id: str


class AirflowTriggerRequest(BaseModel):
    """Schema for triggering an execution from Apache Airflow."""
    pipeline_id: str
    dag_id: str
    dag_run_id: str
    task_id: Optional[str] = None
    run_conf: Dict[str, Any] = Field(default_factory=dict)


class AirflowCallbackRequest(BaseModel):
    """Schema for processing Airflow run callbacks."""
    execution_id: str
    callback_type: AirflowCallbackTypeSchema
    callback_type: str = Field(description="success, failure, retry, running, cancelled")
    dag_id: str
    dag_run_id: str
    task_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None


class LogEntryResponse(BaseModel):
    """Schema for log entry response"""
    id: str
    execution_id: str
    stage_id: Optional[str]
    level: LogLevelSchema
    message: str
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class ExecutionResponse(BaseModel):
    """Schema for execution response"""
    id: str
    pipeline_id: str
    status: ExecutionStatusSchema
    started_at: datetime
    completed_at: Optional[datetime]
    error: Optional[str]
    stages_completed: int
    total_stages: int
    duration: Optional[float]
    context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class ExecutionDetailResponse(ExecutionResponse):
    """Schema for detailed execution response with logs"""
    logs: List[LogEntryResponse]


class ExecutionListResponse(BaseModel):
    """Schema for execution list response"""
    executions: List[ExecutionResponse]
    total: int


# Metrics Schemas
class MetricResponse(BaseModel):
    """Schema for metric response"""
    name: str
    value: float
    unit: Optional[str] = None
    timestamp: datetime


class SystemMetricsResponse(BaseModel):
    """Schema for system metrics response"""
    cpu_usage: float
    memory_usage: float
    pipeline_throughput: int
    active_executions: int
    failure_rate: float
    total_pipelines: int
    success_rate: float
    avg_duration: float
    timestamp: datetime


class MetricsHistoryResponse(BaseModel):
    """Schema for metrics history response"""
    metrics: List[MetricResponse]
    period: str
    start_time: datetime
    end_time: datetime


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error responses"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Success Schemas
class SuccessResponse(BaseModel):
    """Schema for success responses"""
    message: str
    data: Optional[Dict[str, Any]] = None
