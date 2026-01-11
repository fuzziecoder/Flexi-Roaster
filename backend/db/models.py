"""
SQLAlchemy Database Models
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.db.database import Base


class PipelineDB(Base):
    """Pipeline database model"""
    __tablename__ = "pipelines"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    version = Column(String, default="1.0")
    definition = Column(JSON, nullable=False)  # Stores stages and variables
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    executions = relationship("ExecutionDB", back_populates="pipeline", cascade="all, delete-orphan")


class ExecutionDB(Base):
    """Execution database model"""
    __tablename__ = "executions"
    
    id = Column(String, primary_key=True, index=True)
    pipeline_id = Column(String, ForeignKey("pipelines.id"), nullable=False)
    pipeline_name = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    context = Column(JSON, default=lambda: {})  # Execution context/variables
    error = Column(Text, nullable=True)
    
    # Relationships
    pipeline = relationship("PipelineDB", back_populates="executions")
    stage_executions = relationship("StageExecutionDB", back_populates="execution", cascade="all, delete-orphan")
    logs = relationship("LogDB", back_populates="execution", cascade="all, delete-orphan")


class StageExecutionDB(Base):
    """Stage execution database model"""
    __tablename__ = "stage_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String, ForeignKey("executions.id"), nullable=False)
    stage_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    output = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Relationships
    execution = relationship("ExecutionDB", back_populates="stage_executions")


class LogDB(Base):
    """Log database model"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String, ForeignKey("executions.id"), nullable=False)
    level = Column(String, default="info")  # info, warn, error, debug
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    execution = relationship("ExecutionDB", back_populates="logs")


class MetricDB(Base):
    """Metric database model"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_type = Column(String, nullable=False)  # cpu, memory, throughput, etc.
    value = Column(Float, nullable=False)
    unit = Column(String, default="")
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_metadata = Column(JSON, default=lambda: {})  # Additional metric data
