"""
Pydantic Schemas for FlexiRoaster API.
Request/Response models for all endpoints.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


# ===================
# Enums
# ===================

class ExecutionStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class StageTypeEnum(str, Enum):
    INPUT = "input"
    TRANSFORM = "transform"
    VALIDATION = "validation"
    OUTPUT = "output"


class LogLevelEnum(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class InsightSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ===================
# Stage Schemas
# ===================

class StageBase(BaseModel):
    """Base stage schema"""
    id: str
    name: str
    type: StageTypeEnum
    description: Optional[str] = None
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    timeout: int = 120
    max_retries: int = 3
    retry_delay: float = 1.0
    is_critical: bool = True


class StageCreate(StageBase):
    """Schema for creating a stage"""
    pass


class StageResponse(StageBase):
    """Stage response schema"""
    order: int = 0
    
    class Config:
        from_attributes = True


# ===================
# Pipeline Schemas
# ===================

class PipelineBase(BaseModel):
    """Base pipeline schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    version: str = "1.0.0"


class PipelineCreate(PipelineBase):
    """Schema for creating a pipeline"""
    stages: List[StageCreate]
    config: Dict[str, Any] = Field(default_factory=dict)
    schedule: Optional[str] = None  # Cron expression


class PipelineUpdate(BaseModel):
    """Schema for updating a pipeline"""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    stages: Optional[List[StageCreate]] = None
    config: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    is_active: Optional[bool] = None


class PipelineResponse(PipelineBase):
    """Pipeline response schema"""
    id: str
    is_active: bool = True
    schedule: Optional[str] = None
    stage_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PipelineDetailResponse(PipelineResponse):
    """Detailed pipeline response with stages"""
    stages: List[StageResponse] = []
    config: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class PipelineListResponse(BaseModel):
    """Response for listing pipelines"""
    pipelines: List[PipelineResponse]
    total: int


# ===================
# Execution Schemas
# ===================

class ExecutionCreate(BaseModel):
    """Schema for starting an execution"""
    pipeline_id: str
    variables: Dict[str, Any] = Field(default_factory=dict)
    triggered_by: str = "api"


class ExecutionResponse(BaseModel):
    """Execution response schema"""
    id: str
    pipeline_id: Optional[str] = None
    pipeline_name: str
    status: ExecutionStatusEnum
    total_stages: int
    completed_stages: int
    progress: float = 0.0
    risk_score: Optional[float] = None
    triggered_by: str = "manual"
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    error: Optional[str] = None
    
    class Config:
        from_attributes = True


class StageExecutionResponse(BaseModel):
    """Stage execution response schema"""
    stage_id: str
    stage_name: str
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    retry_count: int = 0
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    is_anomaly: bool = False
    
    class Config:
        from_attributes = True


class ExecutionDetailResponse(ExecutionResponse):
    """Detailed execution response with stages and logs"""
    stage_executions: List[StageExecutionResponse] = []
    current_stage: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class ExecutionListResponse(BaseModel):
    """Response for listing executions"""
    executions: List[ExecutionResponse]
    total: int


class ExecutionStartResponse(BaseModel):
    """Response when starting an execution"""
    success: bool
    execution_id: Optional[str] = None
    status: str
    error: Optional[str] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    message: str = ""


class ExecutionStopResponse(BaseModel):
    """Response when stopping an execution"""
    success: bool
    message: str


# ===================
# Log Schemas
# ===================

class LogResponse(BaseModel):
    """Log entry response schema"""
    id: int
    level: LogLevelEnum
    message: str
    stage_id: Optional[str] = None
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class LogListResponse(BaseModel):
    """Response for listing logs"""
    logs: List[LogResponse]
    total: int


# ===================
# AI Insight Schemas
# ===================

class AIInsightResponse(BaseModel):
    """AI insight response schema"""
    id: int
    pipeline_id: Optional[str] = None
    execution_id: Optional[str] = None
    stage_id: Optional[str] = None
    insight_type: str
    severity: InsightSeverityEnum
    title: str
    message: str
    recommendation: Optional[str] = None
    confidence: float
    risk_score: Optional[float] = None
    factors: List[Dict[str, Any]] = []
    explanation: Optional[str] = None
    action_taken: Optional[str] = None
    is_resolved: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIInsightListResponse(BaseModel):
    """Response for listing AI insights"""
    insights: List[AIInsightResponse]
    total: int


class RiskAssessmentResponse(BaseModel):
    """Risk assessment response schema"""
    risk_score: float
    risk_level: str
    should_block: bool
    factors: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    explanation: str = ""


# ===================
# Health Check Schemas
# ===================

class ServiceHealth(BaseModel):
    """Individual service health"""
    status: str
    latency_ms: Optional[float] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    """Health check response schema"""
    status: str
    app: str
    version: str
    timestamp: datetime
    services: Dict[str, ServiceHealth] = Field(default_factory=dict)


# ===================
# Metrics Schemas
# ===================

class MetricResponse(BaseModel):
    """Metric response schema"""
    metric_type: str
    metric_name: str
    value: float
    unit: str = ""
    timestamp: datetime
    tags: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    """Dashboard metrics response"""
    total_pipelines: int
    active_pipelines: int
    total_executions: int
    successful_executions: int
    failed_executions: int
    success_rate: float
    avg_duration: float
    recent_insights: List[AIInsightResponse] = []


# ===================
# Generic Responses
# ===================

class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseModel):
    """Generic error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# ===================
# Airflow Callback Schemas
# ===================

class AirflowCallbackRequest(BaseModel):
    """Airflow DAG callback request"""
    dag_id: str
    dag_run_id: str
    task_id: str
    execution_date: str
    callback_type: str  # success, failure, retry
    context: Dict[str, Any] = Field(default_factory=dict)
