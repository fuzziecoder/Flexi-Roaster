"""
Pipeline Executor for FlexiRoaster.
Handles the actual execution of pipeline stages with data passing and error handling.
"""
import traceback
from datetime import datetime
from typing import Dict, Any, Optional

from backend.models.pipeline import Pipeline, Stage, Execution, ExecutionStatus, LogLevel, StageType
from backend.core.pipeline_engine import PipelineEngine


class PipelineExecutor:
    """Executes pipeline stages sequentially with proper error handling"""
    
    def __init__(self):
        self.engine = PipelineEngine()
    
    def execute(self, pipeline: Pipeline) -> Execution:
        """
        Execute a complete pipeline.
        
        Args:
            pipeline: Pipeline to execute
            
        Returns:
            Execution object with results and logs
        """
        # Validate pipeline first
        is_valid, errors = self.engine.validate_pipeline(pipeline)
        if not is_valid:
            raise ValueError(f"Invalid pipeline: {', '.join(errors)}")
        
        # Create execution context
        execution = self.engine.create_execution_context(pipeline)
        execution.status = ExecutionStatus.RUNNING
        execution.add_log(None, LogLevel.INFO, f"Starting pipeline execution: {pipeline.name}")
        
        try:
            # Get execution order (topological sort)
            execution_order = self.engine.get_execution_order(pipeline)
            execution.add_log(None, LogLevel.INFO, f"Execution order: {' -> '.join(execution_order)}")
            
            # Execute stages in order
            for stage_id in execution_order:
                stage = pipeline.get_stage(stage_id)
                if not stage:
                    raise ValueError(f"Stage not found: {stage_id}")
                
                # Execute stage
                self._execute_stage(stage, execution)
                execution.stages_completed += 1
            
            # Mark as completed
            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.now()
            execution.add_log(
                None, 
                LogLevel.INFO, 
                f"Pipeline completed successfully in {execution.duration:.2f}s"
            )
            
        except Exception as e:
            # Handle execution failure
            execution.status = ExecutionStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error = str(e)
            execution.add_log(
                None,
                LogLevel.ERROR,
                f"Pipeline execution failed: {str(e)}",
                metadata={"traceback": traceback.format_exc()}
            )
        
        return execution
    
    def _execute_stage(self, stage: Stage, execution: Execution) -> None:
        """
        Execute a single stage.
        
        Args:
            stage: Stage to execute
            execution: Current execution context
        """
        execution.add_log(stage.id, LogLevel.INFO, f"Starting stage: {stage.name}")
        
        try:
            # Execute based on stage type
            if stage.type == StageType.INPUT:
                result = self._execute_input_stage(stage, execution)
            elif stage.type == StageType.TRANSFORM:
                result = self._execute_transform_stage(stage, execution)
            elif stage.type == StageType.OUTPUT:
                result = self._execute_output_stage(stage, execution)
            elif stage.type == StageType.VALIDATION:
                result = self._execute_validation_stage(stage, execution)
            else:
                raise ValueError(f"Unknown stage type: {stage.type}")
            
            # Store result in context
            execution.context[stage.id] = result
            
            execution.add_log(
                stage.id,
                LogLevel.INFO,
                f"Stage completed successfully",
                metadata={"result_keys": list(result.keys()) if isinstance(result, dict) else None}
            )
            
        except Exception as e:
            execution.add_log(
                stage.id,
                LogLevel.ERROR,
                f"Stage failed: {str(e)}",
                metadata={"traceback": traceback.format_exc()}
            )
            raise
    
    def _execute_input_stage(self, stage: Stage, execution: Execution) -> Dict[str, Any]:
        """Execute an input stage (data loading)"""
        execution.add_log(stage.id, LogLevel.DEBUG, f"Executing INPUT stage with config: {stage.config}")
        
        # Simulate data loading
        # In a real implementation, this would read from files, databases, APIs, etc.
        source = stage.config.get('source', 'unknown')
        
        # Mock data for demonstration
        data = {
            'source': source,
            'records': [],
            'count': 0
        }
        
        # If source is a file path, we could read it here
        if 'data' in stage.config:
            data['records'] = stage.config['data']
            data['count'] = len(stage.config['data'])
        
        execution.add_log(stage.id, LogLevel.INFO, f"Loaded {data['count']} records from {source}")
        
        return data
    
    def _execute_transform_stage(self, stage: Stage, execution: Execution) -> Dict[str, Any]:
        """Execute a transform stage (data processing)"""
        execution.add_log(stage.id, LogLevel.DEBUG, f"Executing TRANSFORM stage with config: {stage.config}")
        
        # Get input data from dependencies
        input_data = self._get_dependency_data(stage, execution)
        
        # Apply transformations
        # In a real implementation, this would apply various transformations
        operation = stage.config.get('operation', 'passthrough')
        
        result = {
            'operation': operation,
            'input_count': input_data.get('count', 0),
            'output_count': input_data.get('count', 0),
            'data': input_data.get('records', [])
        }
        
        execution.add_log(
            stage.id,
            LogLevel.INFO,
            f"Transformed {result['input_count']} records using {operation}"
        )
        
        return result
    
    def _execute_validation_stage(self, stage: Stage, execution: Execution) -> Dict[str, Any]:
        """Execute a validation stage (data validation)"""
        execution.add_log(stage.id, LogLevel.DEBUG, f"Executing VALIDATION stage with config: {stage.config}")
        
        # Get input data from dependencies
        input_data = self._get_dependency_data(stage, execution)
        
        # Validate data
        schema = stage.config.get('schema', {})
        records = input_data.get('data', [])
        
        valid_count = len(records)  # Simplified - assume all valid
        invalid_count = 0
        
        result = {
            'total': len(records),
            'valid': valid_count,
            'invalid': invalid_count,
            'schema': schema
        }
        
        execution.add_log(
            stage.id,
            LogLevel.INFO,
            f"Validated {valid_count}/{len(records)} records"
        )
        
        return result
    
    def _execute_output_stage(self, stage: Stage, execution: Execution) -> Dict[str, Any]:
        """Execute an output stage (data writing)"""
        execution.add_log(stage.id, LogLevel.DEBUG, f"Executing OUTPUT stage with config: {stage.config}")
        
        # Get input data from dependencies
        input_data = self._get_dependency_data(stage, execution)
        
        # Write data
        # In a real implementation, this would write to files, databases, APIs, etc.
        destination = stage.config.get('destination', 'unknown')
        records = input_data.get('data', [])
        
        result = {
            'destination': destination,
            'records_written': len(records),
            'success': True
        }
        
        execution.add_log(
            stage.id,
            LogLevel.INFO,
            f"Wrote {len(records)} records to {destination}"
        )
        
        return result
    
    def _get_dependency_data(self, stage: Stage, execution: Execution) -> Dict[str, Any]:
        """Get combined data from all stage dependencies"""
        if not stage.dependencies:
            return {}
        
        # For simplicity, return data from the first dependency
        # In a real implementation, you might merge data from multiple dependencies
        first_dep = stage.dependencies[0]
        return execution.context.get(first_dep, {})
