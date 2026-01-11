"""
Pipeline Engine for FlexiRoaster.
Handles pipeline definition parsing, validation, and execution context management.
"""
import yaml
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from backend.models.pipeline import Pipeline, Stage, StageType, Execution, ExecutionStatus, LogLevel


class PipelineEngine:
    """Core engine for managing pipeline definitions"""
    
    @staticmethod
    def parse_pipeline(file_path: str) -> Pipeline:
        """
        Parse a pipeline definition from YAML or JSON file.
        
        Args:
            file_path: Path to the pipeline definition file
            
        Returns:
            Pipeline object
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file format is invalid
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Pipeline file not found: {file_path}")
        
        # Read file content
        content = path.read_text()
        
        # Parse based on file extension
        if path.suffix in ['.yaml', '.yml']:
            data = yaml.safe_load(content)
        elif path.suffix == '.json':
            data = json.loads(content)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}. Use .yaml, .yml, or .json")
        
        return PipelineEngine._dict_to_pipeline(data)
    
    @staticmethod
    def _dict_to_pipeline(data: Dict[str, Any]) -> Pipeline:
        """Convert dictionary to Pipeline object"""
        # Validate required fields
        required_fields = ['name', 'description', 'stages']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Parse stages
        stages = []
        for stage_data in data['stages']:
            stage = Stage(
                id=stage_data.get('id', str(uuid.uuid4())),
                name=stage_data['name'],
                type=StageType(stage_data['type']),
                config=stage_data.get('config', {}),
                dependencies=stage_data.get('dependencies', [])
            )
            stages.append(stage)
        
        # Create pipeline
        pipeline = Pipeline(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
            description=data['description'],
            stages=stages
        )
        
        return pipeline
    
    @staticmethod
    def validate_pipeline(pipeline: Pipeline) -> tuple[bool, List[str]]:
        """
        Validate a pipeline definition.
        
        Args:
            pipeline: Pipeline object to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if pipeline has at least one stage
        if not pipeline.stages:
            errors.append("Pipeline must have at least one stage")
        
        # Check for duplicate stage IDs
        stage_ids = [stage.id for stage in pipeline.stages]
        if len(stage_ids) != len(set(stage_ids)):
            errors.append("Duplicate stage IDs found")
        
        # Validate stage dependencies
        for stage in pipeline.stages:
            for dep_id in stage.dependencies:
                if dep_id not in stage_ids:
                    errors.append(f"Stage '{stage.id}' has invalid dependency: '{dep_id}'")
        
        # Check for circular dependencies
        if PipelineEngine._has_circular_dependencies(pipeline):
            errors.append("Circular dependencies detected in pipeline")
        
        return (len(errors) == 0, errors)
    
    @staticmethod
    def _has_circular_dependencies(pipeline: Pipeline) -> bool:
        """Check if pipeline has circular dependencies using DFS"""
        # Build adjacency list
        graph = {stage.id: stage.dependencies for stage in pipeline.stages}
        
        visited = set()
        rec_stack = set()
        
        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for stage_id in graph:
            if stage_id not in visited:
                if dfs(stage_id):
                    return True
        
        return False
    
    @staticmethod
    def create_execution_context(pipeline: Pipeline) -> Execution:
        """
        Create a new execution context for a pipeline.
        
        Args:
            pipeline: Pipeline to execute
            
        Returns:
            Execution object
        """
        execution = Execution(
            id=f"exec-{uuid.uuid4()}",
            pipeline_id=pipeline.id,
            status=ExecutionStatus.PENDING,
            started_at=datetime.now(),
            total_stages=len(pipeline.stages)
        )
        
        execution.add_log(
            stage_id=None,
            level=LogLevel.INFO,
            message=f"Created execution context for pipeline: {pipeline.name}"
        )
        
        return execution
    
    @staticmethod
    def get_execution_order(pipeline: Pipeline) -> List[str]:
        """
        Get the execution order of stages based on dependencies.
        Uses topological sort.
        
        Args:
            pipeline: Pipeline object
            
        Returns:
            List of stage IDs in execution order
        """
        # Build adjacency list and in-degree count
        graph = {stage.id: stage.dependencies for stage in pipeline.stages}
        in_degree = {stage.id: 0 for stage in pipeline.stages}
        
        for stage in pipeline.stages:
            for dep in stage.dependencies:
                in_degree[stage.id] += 1
        
        # Find all stages with no dependencies
        queue = [stage_id for stage_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            # Get stage with no dependencies
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree for dependent stages
            for stage in pipeline.stages:
                if current in stage.dependencies:
                    in_degree[stage.id] -= 1
                    if in_degree[stage.id] == 0:
                        queue.append(stage.id)
        
        return result
