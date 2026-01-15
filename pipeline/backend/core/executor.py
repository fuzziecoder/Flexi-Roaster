"""
Enhanced Pipeline Executor for FlexiRoaster.
Handles pipeline execution with Redis state management, AI safety, and graceful shutdown.
"""
import asyncio
import logging
import traceback
import signal
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

from config import settings
from core.redis_state import redis_state_manager, ExecutionState
from ai.safety_engine import ai_safety_engine, SafeAction, PipelineStats, RiskAssessment
from db import (
    get_db, ExecutionDB, StageExecutionDB, LogDB, AIInsightDB,
    ExecutionCRUD, StageExecutionCRUD, LogCRUD, AIInsightCRUD, MetricCRUD,
    ExecutionStatus
)

logger = logging.getLogger(__name__)


@dataclass
class StageConfig:
    """Stage configuration for execution"""
    id: str
    name: str
    stage_type: str
    config: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout: int = 120
    max_retries: int = 3
    retry_delay: float = 1.0
    is_critical: bool = True


@dataclass
class ExecutionContext:
    """Context for pipeline execution"""
    execution_id: str
    pipeline_id: str
    pipeline_name: str
    stages: List[StageConfig]
    variables: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    current_stage: Optional[str] = None
    completed_stages: int = 0
    is_cancelled: bool = False
    is_paused: bool = False


class PipelineExecutor:
    """
    Production-grade pipeline executor with:
    - Redis state management
    - AI safety integration
    - Graceful shutdown handling
    - Distributed locking
    - Heartbeat monitoring
    """
    
    def __init__(self):
        self._shutdown_event = asyncio.Event()
        self._active_executions: Dict[str, ExecutionContext] = {}
        self._heartbeat_tasks: Dict[str, asyncio.Task] = {}
        
        # Stage handlers registry
        self._stage_handlers: Dict[str, Callable] = {
            "input": self._execute_input_stage,
            "transform": self._execute_transform_stage,
            "validation": self._execute_validation_stage,
            "output": self._execute_output_stage,
        }
    
    async def initialize(self):
        """Initialize executor and Redis connection"""
        await redis_state_manager.initialize()
        logger.info("Pipeline executor initialized")
    
    async def shutdown(self):
        """Graceful shutdown of executor"""
        logger.info("Initiating graceful shutdown...")
        self._shutdown_event.set()
        
        # Cancel all heartbeat tasks
        for task in self._heartbeat_tasks.values():
            task.cancel()
        
        # Wait for active executions to complete or timeout
        if self._active_executions:
            logger.info(f"Waiting for {len(self._active_executions)} active executions...")
            await asyncio.sleep(5)  # Give executions time to complete
        
        # Mark remaining executions as failed
        for execution_id in list(self._active_executions.keys()):
            await self._mark_execution_failed(
                execution_id,
                "Executor shutdown - execution interrupted"
            )
        
        await redis_state_manager.close()
        logger.info("Pipeline executor shutdown complete")
    
    # ==================
    # Main Execution Flow
    # ==================
    
    async def execute_pipeline(
        self,
        pipeline_id: str,
        pipeline_name: str,
        stages: List[Dict[str, Any]],
        variables: Optional[Dict[str, Any]] = None,
        triggered_by: str = "manual",
        trigger_metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Execute a pipeline with full safety and state management.
        
        Returns execution result with status, logs, and insights.
        """
        execution_id = f"exec-{datetime.now().strftime('%Y%m%d%H%M%S')}-{pipeline_id[:8]}"
        
        try:
            # Check for duplicate runs
            is_duplicate = await redis_state_manager.prevent_duplicate_run(pipeline_id)
            if is_duplicate:
                return {
                    "success": False,
                    "execution_id": None,
                    "error": "Pipeline is already running",
                    "status": "rejected"
                }
            
            # Create stage configs
            stage_configs = [
                StageConfig(
                    id=s["id"],
                    name=s["name"],
                    stage_type=s["type"],
                    config=s.get("config", {}),
                    dependencies=s.get("dependencies", []),
                    timeout=s.get("timeout", settings.EXECUTOR_STAGE_TIMEOUT),
                    max_retries=s.get("max_retries", settings.EXECUTOR_MAX_RETRIES),
                    retry_delay=s.get("retry_delay", settings.EXECUTOR_RETRY_DELAY),
                    is_critical=s.get("is_critical", True)
                )
                for s in stages
            ]
            
            # Create execution context
            context = ExecutionContext(
                execution_id=execution_id,
                pipeline_id=pipeline_id,
                pipeline_name=pipeline_name,
                stages=stage_configs,
                variables=variables or {}
            )
            
            # Pre-execution AI risk assessment
            risk_assessment = await self._assess_pre_execution_risk(pipeline_id, pipeline_name, len(stages))
            
            if risk_assessment.should_block:
                return {
                    "success": False,
                    "execution_id": execution_id,
                    "error": "Execution blocked due to high risk",
                    "status": "blocked",
                    "risk_assessment": {
                        "risk_score": risk_assessment.risk_score,
                        "risk_level": risk_assessment.risk_level,
                        "explanation": risk_assessment.explanation
                    }
                }
            
            # Create execution record in database
            with get_db() as db:
                execution = ExecutionCRUD.create(
                    db=db,
                    id=execution_id,
                    pipeline_id=pipeline_id,
                    pipeline_name=pipeline_name,
                    total_stages=len(stages),
                    triggered_by=triggered_by,
                    variables=variables,
                    trigger_metadata=trigger_metadata,
                    risk_score=risk_assessment.risk_score
                )
                
                # Create stage execution records
                for stage in stage_configs:
                    StageExecutionCRUD.create(
                        db=db,
                        execution_id=execution_id,
                        stage_id=stage.id,
                        stage_name=stage.name
                    )
                
                # Log start
                LogCRUD.create(
                    db=db,
                    execution_id=execution_id,
                    level="info",
                    message=f"Starting pipeline execution: {pipeline_name}"
                )
                
                # Store AI insights
                for insight in ai_safety_engine.generate_insights(
                    PipelineStats(
                        pipeline_id=pipeline_id,
                        pipeline_name=pipeline_name,
                        stage_count=len(stages)
                    ),
                    risk_assessment
                ):
                    if insight.get("severity") in ["high", "critical"]:
                        AIInsightCRUD.create(
                            db=db,
                            pipeline_id=pipeline_id,
                            execution_id=execution_id,
                            insight_type=insight["type"],
                            severity=insight["severity"],
                            title=insight["title"],
                            message=insight["message"],
                            recommendation=insight.get("recommendation"),
                            confidence=insight.get("confidence", 0),
                            factors=insight.get("factors", []),
                            explanation=insight.get("explanation")
                        )
            
            # Execute with lock
            async with redis_state_manager.acquire_execution_lock(execution_id):
                self._active_executions[execution_id] = context
                
                # Start heartbeat
                self._heartbeat_tasks[execution_id] = asyncio.create_task(
                    self._heartbeat_loop(execution_id)
                )
                
                # Set state to running
                await redis_state_manager.set_execution_state(
                    execution_id,
                    ExecutionState.RUNNING,
                    {"started_at": datetime.now().isoformat()}
                )
                
                try:
                    # Execute stages
                    result = await self._execute_stages(context)
                    return result
                    
                finally:
                    # Cleanup
                    if execution_id in self._heartbeat_tasks:
                        self._heartbeat_tasks[execution_id].cancel()
                        del self._heartbeat_tasks[execution_id]
                    
                    if execution_id in self._active_executions:
                        del self._active_executions[execution_id]
                    
                    await redis_state_manager.release_pipeline_lock(pipeline_id)
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            await self._mark_execution_failed(execution_id, str(e))
            return {
                "success": False,
                "execution_id": execution_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def _execute_stages(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute all stages in order with proper error handling"""
        execution_id = context.execution_id
        execution_order = self._get_execution_order(context.stages)
        
        with get_db() as db:
            ExecutionCRUD.update_status(
                db, execution_id, ExecutionStatus.RUNNING
            )
            LogCRUD.create(
                db, execution_id, "info",
                f"Execution order: {' -> '.join(execution_order)}"
            )
        
        for stage_id in execution_order:
            # Check for shutdown or cancellation
            if self._shutdown_event.is_set() or context.is_cancelled:
                await self._handle_cancellation(context)
                return {
                    "success": False,
                    "execution_id": execution_id,
                    "status": "cancelled",
                    "completed_stages": context.completed_stages
                }
            
            # Check for pause
            while context.is_paused:
                await asyncio.sleep(1)
                if self._shutdown_event.is_set():
                    break
            
            # Get stage config
            stage = next((s for s in context.stages if s.id == stage_id), None)
            if not stage:
                raise ValueError(f"Stage not found: {stage_id}")
            
            context.current_stage = stage_id
            
            # Execute stage with retries
            success = await self._execute_stage_with_retry(context, stage)
            
            if not success:
                # AI determines safe action
                action, explanation = ai_safety_engine.select_safe_action(
                    context={
                        "error": context.results.get(stage_id, {}).get("error"),
                        "risk_level": "medium"
                    },
                    is_stage_critical=stage.is_critical,
                    retry_count=settings.EXECUTOR_MAX_RETRIES,
                    max_retries=settings.EXECUTOR_MAX_RETRIES
                )
                
                if action == SafeAction.SKIP_STAGE:
                    with get_db() as db:
                        LogCRUD.create(
                            db, execution_id, "warning",
                            f"Skipping non-critical stage {stage_id}: {explanation}",
                            stage_id=stage_id
                        )
                    continue
                elif action == SafeAction.ROLLBACK:
                    await self._perform_rollback(context)
                    return {
                        "success": False,
                        "execution_id": execution_id,
                        "status": "rolled_back",
                        "completed_stages": context.completed_stages,
                        "error": f"Rolled back after stage {stage_id} failure"
                    }
                elif action in [SafeAction.PAUSE_PIPELINE, SafeAction.TERMINATE]:
                    error_msg = f"Stage {stage_id} failed: {explanation}"
                    await self._mark_execution_failed(execution_id, error_msg)
                    return {
                        "success": False,
                        "execution_id": execution_id,
                        "status": "failed",
                        "completed_stages": context.completed_stages,
                        "error": error_msg
                    }
            
            context.completed_stages += 1
            
            # Update state
            await redis_state_manager.set_execution_state(
                execution_id,
                ExecutionState.RUNNING,
                {"completed_stages": context.completed_stages}
            )
        
        # Mark completed
        await self._mark_execution_completed(context)
        
        return {
            "success": True,
            "execution_id": execution_id,
            "status": "completed",
            "completed_stages": context.completed_stages,
            "results": context.results
        }
    
    async def _execute_stage_with_retry(
        self,
        context: ExecutionContext,
        stage: StageConfig
    ) -> bool:
        """Execute a stage with retry logic"""
        execution_id = context.execution_id
        stage_id = stage.id
        
        for attempt in range(stage.max_retries + 1):
            try:
                # Track retry count in Redis
                if attempt > 0:
                    await redis_state_manager.increment_retry_counter(
                        execution_id, stage_id
                    )
                    with get_db() as db:
                        LogCRUD.create(
                            db, execution_id, "warning",
                            f"Retrying stage {stage_id} (attempt {attempt + 1}/{stage.max_retries + 1})",
                            stage_id=stage_id
                        )
                    await asyncio.sleep(stage.retry_delay * (settings.EXECUTOR_RETRY_BACKOFF ** attempt))
                
                # Update stage state
                await redis_state_manager.set_stage_state(
                    execution_id, stage_id, "running"
                )
                
                with get_db() as db:
                    StageExecutionCRUD.update(
                        db, execution_id, stage_id,
                        status="running",
                        started_at=datetime.now(),
                        retry_count=attempt
                    )
                    LogCRUD.create(
                        db, execution_id, "info",
                        f"Starting stage: {stage.name}",
                        stage_id=stage_id
                    )
                
                # Execute with timeout
                start_time = datetime.now()
                handler = self._stage_handlers.get(stage.stage_type, self._execute_generic_stage)
                
                try:
                    result = await asyncio.wait_for(
                        handler(stage, context),
                        timeout=stage.timeout
                    )
                except asyncio.TimeoutError:
                    raise TimeoutError(f"Stage {stage_id} timed out after {stage.timeout}s")
                
                duration = (datetime.now() - start_time).total_seconds()
                
                # Store result
                context.results[stage_id] = result
                
                # Update database
                with get_db() as db:
                    StageExecutionCRUD.update(
                        db, execution_id, stage_id,
                        status="completed",
                        completed_at=datetime.now(),
                        duration=duration,
                        output=result
                    )
                    LogCRUD.create(
                        db, execution_id, "info",
                        f"Stage completed in {duration:.2f}s",
                        stage_id=stage_id,
                        metadata={"duration": duration}
                    )
                    
                    # Record metric
                    MetricCRUD.record(
                        db, "stage_duration", stage_id,
                        duration, "seconds",
                        pipeline_id=context.pipeline_id,
                        execution_id=execution_id
                    )
                
                await redis_state_manager.set_stage_state(
                    execution_id, stage_id, "completed", output=result
                )
                
                # Reset retry counter on success
                await redis_state_manager.reset_retry_counter(execution_id, stage_id)
                
                return True
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Stage {stage_id} failed (attempt {attempt + 1}): {error_msg}")
                
                with get_db() as db:
                    LogCRUD.create(
                        db, execution_id, "error",
                        f"Stage failed: {error_msg}",
                        stage_id=stage_id,
                        metadata={"traceback": traceback.format_exc()}
                    )
                
                await redis_state_manager.set_stage_state(
                    execution_id, stage_id, "failed", error=error_msg
                )
                
                context.results[stage_id] = {"error": error_msg}
                
                # Check if should retry
                if attempt >= stage.max_retries:
                    with get_db() as db:
                        StageExecutionCRUD.update(
                            db, execution_id, stage_id,
                            status="failed",
                            completed_at=datetime.now(),
                            error=error_msg
                        )
                    return False
        
        return False
    
    # ==================
    # Stage Handlers
    # ==================
    
    async def _execute_input_stage(
        self,
        stage: StageConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute an input stage"""
        config = stage.config
        source = config.get("source", "unknown")
        
        # Simulate data loading
        # In production, this would load from files, databases, APIs
        data = {
            "source": source,
            "records": config.get("data", []),
            "count": len(config.get("data", []))
        }
        
        return data
    
    async def _execute_transform_stage(
        self,
        stage: StageConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute a transform stage"""
        config = stage.config
        operation = config.get("operation", "passthrough")
        
        # Get input from dependencies
        input_data = self._get_dependency_data(stage, context)
        
        # Apply transformation (simplified)
        result = {
            "operation": operation,
            "input_count": input_data.get("count", 0),
            "output_count": input_data.get("count", 0),
            "data": input_data.get("records", [])
        }
        
        return result
    
    async def _execute_validation_stage(
        self,
        stage: StageConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute a validation stage"""
        config = stage.config
        schema = config.get("schema", {})
        
        input_data = self._get_dependency_data(stage, context)
        records = input_data.get("data", [])
        
        return {
            "total": len(records),
            "valid": len(records),
            "invalid": 0,
            "schema": schema
        }
    
    async def _execute_output_stage(
        self,
        stage: StageConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute an output stage"""
        config = stage.config
        destination = config.get("destination", "unknown")
        
        input_data = self._get_dependency_data(stage, context)
        records = input_data.get("data", [])
        
        return {
            "destination": destination,
            "records_written": len(records),
            "success": True
        }
    
    async def _execute_generic_stage(
        self,
        stage: StageConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generic stage handler for unknown types"""
        return {
            "stage_type": stage.stage_type,
            "config": stage.config,
            "status": "executed"
        }
    
    def _get_dependency_data(
        self,
        stage: StageConfig,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Get combined data from stage dependencies"""
        if not stage.dependencies:
            return {}
        
        # Return first dependency's data
        first_dep = stage.dependencies[0]
        return context.results.get(first_dep, {})
    
    def _get_execution_order(self, stages: List[StageConfig]) -> List[str]:
        """Get topological execution order"""
        # Simple implementation - production would use proper toposort
        order = []
        remaining = {s.id: s for s in stages}
        completed = set()
        
        while remaining:
            for stage_id, stage in list(remaining.items()):
                deps = set(stage.dependencies)
                if deps.issubset(completed):
                    order.append(stage_id)
                    completed.add(stage_id)
                    del remaining[stage_id]
                    break
            else:
                # No progress - circular dependency
                raise ValueError(f"Circular dependency detected in stages: {list(remaining.keys())}")
        
        return order
    
    # ==================
    # AI Integration
    # ==================
    
    async def _assess_pre_execution_risk(
        self,
        pipeline_id: str,
        pipeline_name: str,
        stage_count: int
    ) -> RiskAssessment:
        """Perform pre-execution risk assessment"""
        # Get historical stats from database
        with get_db() as db:
            stats_dict = ExecutionCRUD.get_stats(db, pipeline_id, days=30)
        
        stats = PipelineStats(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            total_executions=stats_dict.get("total", 0),
            successful_executions=stats_dict.get("completed", 0),
            failed_executions=stats_dict.get("failed", 0),
            avg_duration=stats_dict.get("avg_duration", 0),
            stage_count=stage_count
        )
        
        return ai_safety_engine.assess_risk(stats)
    
    # ==================
    # State Management
    # ==================
    
    async def _heartbeat_loop(self, execution_id: str):
        """Send periodic heartbeats for an execution"""
        while True:
            try:
                await redis_state_manager.send_heartbeat(execution_id)
                await asyncio.sleep(settings.HEARTBEAT_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Heartbeat error for {execution_id}: {e}")
    
    async def _mark_execution_completed(self, context: ExecutionContext):
        """Mark execution as completed"""
        execution_id = context.execution_id
        
        await redis_state_manager.set_execution_state(
            execution_id,
            ExecutionState.COMPLETED,
            {"completed_at": datetime.now().isoformat()}
        )
        
        with get_db() as db:
            ExecutionCRUD.update_status(
                db, execution_id, ExecutionStatus.COMPLETED,
                completed_stages=context.completed_stages
            )
            LogCRUD.create(
                db, execution_id, "info",
                f"Pipeline completed successfully with {context.completed_stages} stages"
            )
    
    async def _mark_execution_failed(self, execution_id: str, error: str):
        """Mark execution as failed"""
        await redis_state_manager.set_execution_state(
            execution_id,
            ExecutionState.FAILED,
            {"error": error, "failed_at": datetime.now().isoformat()}
        )
        
        with get_db() as db:
            ExecutionCRUD.update_status(
                db, execution_id, ExecutionStatus.FAILED,
                error=error
            )
            LogCRUD.create(
                db, execution_id, "error",
                f"Pipeline execution failed: {error}"
            )
    
    async def _handle_cancellation(self, context: ExecutionContext):
        """Handle execution cancellation"""
        execution_id = context.execution_id
        
        await redis_state_manager.set_execution_state(
            execution_id,
            ExecutionState.CANCELLED,
            {"cancelled_at": datetime.now().isoformat()}
        )
        
        with get_db() as db:
            ExecutionCRUD.update_status(
                db, execution_id, ExecutionStatus.CANCELLED
            )
            LogCRUD.create(
                db, execution_id, "warning",
                "Pipeline execution cancelled"
            )
    
    async def _perform_rollback(self, context: ExecutionContext):
        """Perform pipeline rollback"""
        execution_id = context.execution_id
        
        await redis_state_manager.set_execution_state(
            execution_id,
            ExecutionState.ROLLED_BACK,
            {"rolled_back_at": datetime.now().isoformat()}
        )
        
        with get_db() as db:
            ExecutionCRUD.update_status(
                db, execution_id, ExecutionStatus.ROLLED_BACK
            )
            LogCRUD.create(
                db, execution_id, "warning",
                f"Pipeline rolled back after {context.completed_stages} stages"
            )
            
            # Store rollback insight
            AIInsightCRUD.create(
                db,
                execution_id=execution_id,
                insight_type="anomaly",
                severity="high",
                title="Pipeline Rollback Executed",
                message=f"Pipeline was rolled back after failing at stage {context.current_stage}",
                recommendation="Review logs and fix underlying issues before retry"
            )
    
    # ==================
    # Control Methods
    # ==================
    
    async def stop_execution(self, execution_id: str) -> bool:
        """Stop a running execution"""
        if execution_id in self._active_executions:
            self._active_executions[execution_id].is_cancelled = True
            return True
        return False
    
    async def pause_execution(self, execution_id: str) -> bool:
        """Pause a running execution"""
        if execution_id in self._active_executions:
            self._active_executions[execution_id].is_paused = True
            await redis_state_manager.set_execution_state(
                execution_id, ExecutionState.PAUSED
            )
            return True
        return False
    
    async def resume_execution(self, execution_id: str) -> bool:
        """Resume a paused execution"""
        if execution_id in self._active_executions:
            self._active_executions[execution_id].is_paused = False
            await redis_state_manager.set_execution_state(
                execution_id, ExecutionState.RUNNING
            )
            return True
        return False
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an active execution"""
        context = self._active_executions.get(execution_id)
        if context:
            return {
                "execution_id": execution_id,
                "pipeline_id": context.pipeline_id,
                "status": "paused" if context.is_paused else "running",
                "current_stage": context.current_stage,
                "completed_stages": context.completed_stages,
                "total_stages": len(context.stages)
            }
        return None


# Singleton instance
pipeline_executor = PipelineExecutor()
