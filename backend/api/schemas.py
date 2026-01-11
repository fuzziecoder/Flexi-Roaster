"""
Pydantic schemas for API requests and responses
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from backend.models.pipeline import PipelineStatus, StageStatus


# Pipeline Schemas
class PipelineCreate(BaseModel):
    """Schema for creating a pipeline"""
    name: str
    description: str
    version: str = "1.0"
    stages: List[Dict[str, Any]]
    variables: Dict[str, Any] = Field(default_factory=dict)


class PipelineUpdate(BaseModel):
    """Schema for updating a pipeline"""
    name: Optional[str] = None
    description: Optional[str] = None
    stages: Optional[List[Dict[str, Any]]] = None
    variables: Optional[Dict[str, Any]] = None


class PipelineResponse(BaseModel):
    """Schema for pipeline response"""
    id: str
    name: str
    description: str
    version: str
    stages: List[Dict[str, Any]]
    variables: Dict[str, Any]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Execution Schemas
class ExecutionCreate(BaseModel):
    """Schema for creating an execution"""
    pipeline_id: str
    variables: Optional[Dict[str, Any]] = None


class StageExecutionResponse(BaseModel):
    """Schema for stage execution response"""
    stage_id: str
    status: StageStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration: Optional[float]
    output: Optional[Dict[str, Any]]
    error: Optional[str]


class ExecutionResponse(BaseModel):
    """Schema for execution response"""
    id: str
    pipeline_id: str
    pipeline_name: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration: Optional[float]
    stage_executions: List[StageExecutionResponse] = Field(default_factory=list)
    error: Optional[str]


class ExecutionLogsResponse(BaseModel):
    """Schema for execution logs"""
    execution_id: str
    logs: List[str]


# Metrics Schemas
class MetricValue(BaseModel):
    """Single metric value"""
    name: str
    value: float
    unit: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    """Schema for metrics response"""
    cpu: float
    memory: float
    throughput: float
    active_executions: int
    total_pipelines: int
    success_rate: float
    failure_rate: float
    avg_duration: float
    timestamp: datetime


class MetricsHistoryResponse(BaseModel):
    """Schema for metrics history"""
    metrics: List[MetricsResponse]
    start_time: datetime
    end_time: datetime


# Generic Response
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
