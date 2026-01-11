"""
Pipeline Executor - Executes pipeline stages sequentially
Handles stage lifecycle, data passing, and error handling
"""
import time
import traceback
from typing import Dict, Any, Optional
from datetime import datetime

from backend.models.pipeline import (
    PipelineDefinition,
    PipelineExecution,
    StageExecution,
    StageConfig,
    PipelineStatus,
    StageStatus
)


class StageHandler:
    """Base class for stage handlers"""
    
    def execute(self, stage: StageConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a stage
        
        Args:
            stage: Stage configuration
            context: Execution context (shared data)
            
        Returns:
            Stage output data
        """
        raise NotImplementedError("Subclasses must implement execute()")


class InputStageHandler(StageHandler):
    """Handler for input stages"""
    
    def execute(self, stage: StageConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Read input data"""
        source = stage.config.get('source', 'stdin')
        
        # Simulate reading data
        data = {
            'source': source,
            'records': [
                {'id': 1, 'value': 'data1'},
                {'id': 2, 'value': 'data2'},
            ],
            'count': 2
        }
        
        return data


class TransformStageHandler(StageHandler):
    """Handler for transform stages"""
    
    def execute(self, stage: StageConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data"""
        operation = stage.config.get('operation', 'passthrough')
        
        # Get input from previous stage
        input_data = context.get('previous_output', {})
        
        # Simulate transformation
        transformed = {
            'operation': operation,
            'input_count': input_data.get('count', 0),
            'output_count': input_data.get('count', 0),
            'transformed': True
        }
        
        return transformed


class OutputStageHandler(StageHandler):
    """Handler for output stages"""
    
    def execute(self, stage: StageConfig, context: Dict[str, Any]) -> Dict[str, Any]:
        """Write output data"""
        destination = stage.config.get('destination', 'stdout')
        
        # Get input from previous stage
        input_data = context.get('previous_output', {})
        
        # Simulate writing data
        result = {
            'destination': destination,
            'records_written': input_data.get('output_count', 0),
            'success': True
        }
        
        return result


class PipelineExecutor:
    """Executes pipelines stage by stage"""
    
    def __init__(self):
        # Register stage handlers
        self.handlers: Dict[str, StageHandler] = {
            'input': InputStageHandler(),
            'transform': TransformStageHandler(),
            'output': OutputStageHandler(),
        }
    
    def register_handler(self, stage_type: str, handler: StageHandler):
        """Register a custom stage handler"""
        self.handlers[stage_type] = handler
    
    def execute(self, pipeline: PipelineDefinition, execution: PipelineExecution) -> PipelineExecution:
        """
        Execute a pipeline
        
        Args:
            pipeline: Pipeline definition
            execution: Execution instance
            
        Returns:
            Updated execution with results
        """
        try:
            execution.status = PipelineStatus.RUNNING
            execution.started_at = datetime.utcnow()
            
            # Execute stages in order
            for stage in pipeline.stages:
                # Check dependencies
                if not self._dependencies_met(stage, execution):
                    self._log(execution, f"Skipping stage {stage.id} - dependencies not met")
                    continue
                
                # Execute stage
                stage_execution = self._execute_stage(stage, execution)
                execution.stage_executions.append(stage_execution)
                
                # Check if stage failed
                if stage_execution.status == StageStatus.FAILED:
                    execution.status = PipelineStatus.FAILED
                    execution.error = f"Stage '{stage.id}' failed: {stage_execution.error}"
                    break
                
                # Store output in context for next stage
                if stage_execution.output:
                    execution.context['previous_output'] = stage_execution.output
                    execution.context[f'{stage.id}_output'] = stage_execution.output
            
            # Mark as completed if not failed
            if execution.status == PipelineStatus.RUNNING:
                execution.status = PipelineStatus.COMPLETED
            
            execution.completed_at = datetime.utcnow()
            execution.duration = (execution.completed_at - execution.started_at).total_seconds()
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error = f"Pipeline execution failed: {str(e)}"
            execution.completed_at = datetime.utcnow()
            if execution.started_at:
                execution.duration = (execution.completed_at - execution.started_at).total_seconds()
        
        return execution
    
    def _execute_stage(self, stage: StageConfig, execution: PipelineExecution) -> StageExecution:
        """Execute a single stage"""
        stage_exec = StageExecution(
            stage_id=stage.id,
            status=StageStatus.RUNNING,
            started_at=datetime.utcnow()
        )
        
        try:
            self._log(execution, f"Starting stage: {stage.name} ({stage.id})")
            
            # Get handler for stage type
            handler = self.handlers.get(stage.type)
            if not handler:
                raise ValueError(f"No handler registered for stage type: {stage.type}")
            
            # Execute stage
            output = handler.execute(stage, execution.context)
            
            stage_exec.status = StageStatus.COMPLETED
            stage_exec.output = output
            stage_exec.completed_at = datetime.utcnow()
            stage_exec.duration = (stage_exec.completed_at - stage_exec.started_at).total_seconds()
            
            self._log(execution, f"Completed stage: {stage.name} in {stage_exec.duration:.2f}s")
            
        except Exception as e:
            stage_exec.status = StageStatus.FAILED
            stage_exec.error = str(e)
            stage_exec.completed_at = datetime.utcnow()
            stage_exec.duration = (stage_exec.completed_at - stage_exec.started_at).total_seconds()
            
            error_trace = traceback.format_exc()
            self._log(execution, f"Stage failed: {stage.name}\nError: {str(e)}\n{error_trace}")
        
        return stage_exec
    
    def _dependencies_met(self, stage: StageConfig, execution: PipelineExecution) -> bool:
        """Check if all stage dependencies are met"""
        if not stage.dependencies:
            return True
        
        completed_stages = {
            se.stage_id for se in execution.stage_executions
            if se.status == StageStatus.COMPLETED
        }
        
        return all(dep in completed_stages for dep in stage.dependencies)
    
    def _log(self, execution: PipelineExecution, message: str):
        """Add log message to execution context"""
        if 'logs' not in execution.context:
            execution.context['logs'] = []
        
        log_entry = f"[{datetime.utcnow().isoformat()}] {message}"
        execution.context['logs'].append(log_entry)
        print(log_entry)  # Also print to console
