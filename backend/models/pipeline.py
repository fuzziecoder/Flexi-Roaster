"""
Pipeline data models for FlexiRoaster.
Defines the core data structures for pipelines, stages, and executions.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class StageType(str, Enum):
    """Types of pipeline stages"""
    INPUT = "input"
    TRANSFORM = "transform"
    OUTPUT = "output"
    VALIDATION = "validation"


class ExecutionStatus(str, Enum):
    """Execution status states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


@dataclass
class Stage:
    """Represents a single stage in a pipeline"""
    id: str
    name: str
    type: StageType
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if isinstance(self.type, str):
            self.type = StageType(self.type)


@dataclass
class Pipeline:
    """Represents a complete pipeline definition"""
    id: str
    name: str
    description: str
    stages: List[Stage]
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def get_stage(self, stage_id: str) -> Optional[Stage]:
        """Get a stage by ID"""
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        return None


@dataclass
class LogEntry:
    """Represents a single log entry"""
    id: str
    execution_id: str
    stage_id: Optional[str]
    level: LogLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.level, str):
            self.level = LogLevel(self.level)


@dataclass
class Execution:
    """Represents a pipeline execution instance"""
    id: str
    pipeline_id: str
    status: ExecutionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    logs: List[LogEntry] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    stages_completed: int = 0
    total_stages: int = 0
    
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = ExecutionStatus(self.status)
    
    def add_log(self, stage_id: Optional[str], level: LogLevel, message: str, metadata: Dict[str, Any] = None):
        """Add a log entry to this execution"""
        log_entry = LogEntry(
            id=f"{self.id}-log-{len(self.logs)}",
            execution_id=self.id,
            stage_id=stage_id,
            level=level,
            message=message,
            metadata=metadata or {}
        )
        self.logs.append(log_entry)
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate execution duration in seconds"""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
