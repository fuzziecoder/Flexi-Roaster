"""
FlexiRoaster Pipeline Models
Pydantic models for pipeline definition and execution
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class PipelineStatus(str, Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


class StageStatus(str, Enum):
    """Stage execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class StageConfig(BaseModel):
    """Configuration for a pipeline stage"""
    id: str
    name: str
    type: str  # e.g., "input", "transform", "output"
    config: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[str] = Field(default_factory=list)
    timeout: Optional[int] = 300  # seconds
    retry_count: int = 0


class PipelineDefinition(BaseModel):
    """Pipeline definition from YAML/JSON"""
    id: Optional[str] = None
    name: str
    description: str
    version: str = "1.0"
    stages: List[StageConfig]
    variables: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Data Processing Pipeline",
                "description": "Process customer data",
                "version": "1.0",
                "stages": [
                    {
                        "id": "input",
                        "name": "Read Data",
                        "type": "input",
                        "config": {"source": "data.csv"}
                    }
                ]
            }
        }


class StageExecution(BaseModel):
    """Stage execution result"""
    stage_id: str
    status: StageStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    logs: List[str] = Field(default_factory=list)


class PipelineExecution(BaseModel):
    """Pipeline execution state"""
    id: str
    pipeline_id: str
    pipeline_name: str
    status: PipelineStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[float] = None
    stage_executions: List[StageExecution] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)  # Shared data between stages
    error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "exec-123",
                "pipeline_id": "pipe-456",
                "pipeline_name": "Data Pipeline",
                "status": "running",
                "started_at": "2024-01-10T10:00:00Z"
            }
        }
