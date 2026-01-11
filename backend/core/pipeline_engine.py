"""
Pipeline Engine - Core execution logic
Handles pipeline parsing, validation, and execution
"""
import yaml
import json
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import uuid

from backend.models.pipeline import (
    PipelineDefinition,
    PipelineExecution,
    PipelineStatus,
    StageConfig
)


class PipelineEngine:
    """Core pipeline engine for parsing and managing pipelines"""
    
    def __init__(self):
        self.pipelines: Dict[str, PipelineDefinition] = {}
    
    def load_from_yaml(self, file_path: str) -> PipelineDefinition:
        """Load pipeline definition from YAML file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {file_path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return self._parse_definition(data)
    
    def load_from_json(self, file_path: str) -> PipelineDefinition:
        """Load pipeline definition from JSON file"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {file_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return self._parse_definition(data)
    
    def load_from_dict(self, data: Dict[str, Any]) -> PipelineDefinition:
        """Load pipeline definition from dictionary"""
        return self._parse_definition(data)
    
    def _parse_definition(self, data: Dict[str, Any]) -> PipelineDefinition:
        """Parse and validate pipeline definition"""
        # Generate ID if not provided
        if 'id' not in data or not data['id']:
            data['id'] = f"pipe-{uuid.uuid4().hex[:8]}"
        
        # Validate and create pipeline definition
        pipeline = PipelineDefinition(**data)
        
        # Validate stage dependencies
        self._validate_dependencies(pipeline)
        
        # Store pipeline
        self.pipelines[pipeline.id] = pipeline
        
        return pipeline
    
    def _validate_dependencies(self, pipeline: PipelineDefinition):
        """Validate that all stage dependencies exist"""
        stage_ids = {stage.id for stage in pipeline.stages}
        
        for stage in pipeline.stages:
            for dep in stage.dependencies:
                if dep not in stage_ids:
                    raise ValueError(
                        f"Stage '{stage.id}' has invalid dependency '{dep}'"
                    )
    
    def get_pipeline(self, pipeline_id: str) -> Optional[PipelineDefinition]:
        """Get pipeline by ID"""
        return self.pipelines.get(pipeline_id)
    
    def list_pipelines(self) -> list[PipelineDefinition]:
        """List all loaded pipelines"""
        return list(self.pipelines.values())
    
    def create_execution(self, pipeline_id: str) -> PipelineExecution:
        """Create a new execution instance for a pipeline"""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise ValueError(f"Pipeline not found: {pipeline_id}")
        
        execution = PipelineExecution(
            id=f"exec-{uuid.uuid4().hex[:8]}",
            pipeline_id=pipeline.id,
            pipeline_name=pipeline.name,
            status=PipelineStatus.PENDING,
            started_at=datetime.utcnow(),
            context=pipeline.variables.copy()  # Initialize with pipeline variables
        )
        
        return execution
    
    def validate_pipeline(self, pipeline: PipelineDefinition) -> tuple[bool, Optional[str]]:
        """Validate pipeline definition"""
        try:
            # Check for at least one stage
            if not pipeline.stages:
                return False, "Pipeline must have at least one stage"
            
            # Check for duplicate stage IDs
            stage_ids = [stage.id for stage in pipeline.stages]
            if len(stage_ids) != len(set(stage_ids)):
                return False, "Duplicate stage IDs found"
            
            # Validate dependencies
            self._validate_dependencies(pipeline)
            
            return True, None
        except Exception as e:
            return False, str(e)
