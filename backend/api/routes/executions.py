"""
Execution management API routes.
Handles pipeline execution and execution monitoring.
"""
from typing import Any, Dict, List, Optional
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from backend.api.schemas import (
    ExecutionCreate,
    ExecutionDetailResponse,
    ExecutionListResponse,
    OrchestrationEngineSchema,
    SuccessResponse
)
from backend.models.pipeline import Execution, ExecutionStatus
from backend.core.distributed_executor import DistributedExecutionDispatcher
from backend.core.executor import PipelineExecutor
from backend.core.orchestration import OrchestrationEngine, OrchestrationRequest, OrchestrationRegistry
    ExecutionResponse,
    SuccessResponse,
)
from backend.api.security import UserPrincipal, get_current_user
from backend.config import settings
from backend.core.executor import PipelineExecutor
from backend.events import get_event_publisher
from backend.observability import observability_metrics
from backend.models.pipeline import Execution, ExecutionStatus

router = APIRouter(prefix="/executions", tags=["executions"])

# In-memory storage (will be replaced with database in Phase 3)
executions_db: Dict[str, Execution] = {}

# Import pipelines_db from pipelines route
from backend.api.routes.pipelines import pipelines_db

TERMINAL_STATUSES = {ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED}


def _pipeline_failure_rate_percent(pipeline_id: str) -> float:
    """Compute failure rate for completed pipeline executions."""
    terminal = [
        execution
        for execution in executions_db.values()
        if execution.pipeline_id == pipeline_id and execution.status in TERMINAL_STATUSES
    ]
    if not terminal:
        return 0.0

    failed = len([execution for execution in terminal if execution.status == ExecutionStatus.FAILED])
    return (failed / len(terminal)) * 100


def _update_active_executions_metric() -> None:
    active_count = len([
        execution for execution in executions_db.values()
        if execution.status in {ExecutionStatus.PENDING, ExecutionStatus.RUNNING}
    ])
    observability_metrics.set_active_executions(active_count)
ORCHESTRATION_SCHEMA_TO_CORE = {
    OrchestrationEngineSchema.LOCAL: OrchestrationEngine.LOCAL,
    OrchestrationEngineSchema.AIRFLOW: OrchestrationEngine.AIRFLOW,
    OrchestrationEngineSchema.TEMPORAL: OrchestrationEngine.TEMPORAL,
    OrchestrationEngineSchema.PREFECT: OrchestrationEngine.PREFECT,
}


def _build_orchestration_context(execution_data: ExecutionCreate) -> Dict[str, Any]:
    orchestration = execution_data.orchestration
    return {
        "orchestration": {
            "engine": orchestration.engine.value,
            "retry_attempts": orchestration.retry_attempts,
            "retry_backoff_seconds": orchestration.retry_backoff_seconds,
            "schedule": orchestration.schedule,
            "options": orchestration.options.copy(),
        }
    }


def _merge_execution_context(result_context: Dict[str, Any], existing_context: Dict[str, Any]) -> Dict[str, Any]:
    """Merge contexts with special handling for nested Airflow metadata."""
    merged = result_context.copy()
    merged.update(existing_context)

    if "airflow" in result_context or "airflow" in existing_context:
        airflow_context: Dict[str, Any] = {}
        airflow_context.update(result_context.get("airflow", {}))
        airflow_context.update(existing_context.get("airflow", {}))
        merged["airflow"] = airflow_context

    return merged


def _merge_execution_logs(result_logs: List, existing_logs: List) -> List:
    """Keep existing trigger/callback logs while avoiding duplicates."""
    merged_logs: List = []
    seen_ids = set()

    for log in existing_logs + result_logs:
        if log.id in seen_ids:
            continue
        seen_ids.add(log.id)
        merged_logs.append(log)

    return merged_logs


def initialize_execution(
    pipeline_id: str,
    context: Optional[Dict[str, Any]] = None,
    execution_backend: Optional[str] = None,
) -> Execution:
    """Create and store a pending execution record."""
    user_id: str,
    context: Optional[Dict[str, Any]] = None,
) -> Execution:
    """Create and store a pending execution record for a specific user."""
    from datetime import datetime

    execution_id = f"exec-{uuid.uuid4()}"
    pipeline = pipelines_db[pipeline_id]
    merged_context = context.copy() if context else {}
    if execution_backend:
        merged_context["requested_execution_backend"] = execution_backend

    execution = Execution(
        id=execution_id,
        pipeline_id=pipeline_id,
        user_id=user_id,
        status=ExecutionStatus.PENDING,
        started_at=datetime.now(),
        total_stages=len(pipeline.stages),
        context=merged_context
        context=context or {},
    )
    executions_db[execution_id] = execution
    _update_active_executions_metric()

    get_event_publisher().publish(
        topic=settings.TOPIC_EXECUTION_STARTED,
        key=execution.id,
        payload={
            "execution_id": execution.id,
            "pipeline_id": execution.pipeline_id,
            "status": execution.status.value,
            "total_stages": execution.total_stages,
            "user_id": execution.user_id,
        },
    )
    return execution


async def execute_pipeline_background(
    pipeline_id: str,
    execution_id: str,
    execution_backend: Optional[str] = None,
):
    """Background task to execute pipeline."""
    try:
        pipeline = pipelines_db[pipeline_id]
        dispatcher = DistributedExecutionDispatcher()
        dispatch_result = dispatcher.run(pipeline, backend_override=execution_backend)
        result = dispatch_result.execution
        result.context.setdefault("distributed_execution", {})
        result.context["distributed_execution"]["backend_used"] = dispatch_result.backend_used

        existing = executions_db.get(execution_id)
        if existing:
            result.context = _merge_execution_context(result.context, existing.context)
            result.logs = _merge_execution_logs(result.logs, existing.logs)
            result.started_at = existing.started_at
            result.user_id = existing.user_id

            if existing.status in TERMINAL_STATUSES and existing.context.get("airflow", {}).get("last_callback_type"):
                result.status = existing.status
                result.completed_at = existing.completed_at
                result.error = existing.error

        result.id = execution_id
        if execution_id in executions_db:
            existing_context = executions_db[execution_id].context.copy()
            result.context.update(existing_context)

        result.id = execution_id
        executions_db[execution_id] = result

        observability_metrics.observe_execution_outcome(
            pipeline_id=result.pipeline_id,
            status=result.status.value,
            duration_seconds=result.duration,
            failure_rate_percent=_pipeline_failure_rate_percent(result.pipeline_id),
            sla_target_seconds=settings.PIPELINE_SLA_TARGET_SECONDS,
        )
        _update_active_executions_metric()
        observability_metrics.observe_process_resources()

        if result.status == ExecutionStatus.COMPLETED:
            get_event_publisher().publish(
                topic=settings.TOPIC_EXECUTION_COMPLETED,
                key=result.id,
                payload={
                    "execution_id": result.id,
                    "pipeline_id": result.pipeline_id,
                    "status": result.status.value,
                    "duration_seconds": result.duration,
                    "stages_completed": result.stages_completed,
                    "total_stages": result.total_stages,
                    "user_id": result.user_id,
                },
            )
        elif result.status == ExecutionStatus.FAILED:
            get_event_publisher().publish(
                topic=settings.TOPIC_EXECUTION_FAILED,
                key=result.id,
                payload={
                    "execution_id": result.id,
                    "pipeline_id": result.pipeline_id,
                    "status": result.status.value,
                    "error": result.error,
                    "stages_completed": result.stages_completed,
                    "total_stages": result.total_stages,
                    "user_id": result.user_id,
                },
            )
    except Exception as e:
        if execution_id in executions_db:
            executions_db[execution_id].status = ExecutionStatus.FAILED
            executions_db[execution_id].error = str(e)
            failed_execution = executions_db[execution_id]
            observability_metrics.observe_execution_outcome(
                pipeline_id=failed_execution.pipeline_id,
                status=failed_execution.status.value,
                duration_seconds=failed_execution.duration,
                failure_rate_percent=_pipeline_failure_rate_percent(failed_execution.pipeline_id),
                sla_target_seconds=settings.PIPELINE_SLA_TARGET_SECONDS,
            )
            _update_active_executions_metric()
            observability_metrics.observe_process_resources()
            get_event_publisher().publish(
                topic=settings.TOPIC_EXECUTION_FAILED,
                key=failed_execution.id,
                payload={
                    "execution_id": failed_execution.id,
                    "pipeline_id": failed_execution.pipeline_id,
                    "status": failed_execution.status.value,
                    "error": failed_execution.error,
                    "user_id": failed_execution.user_id,
                },
            )


@router.post(
    "",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start pipeline execution"
)
async def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    current_user: UserPrincipal = Depends(get_current_user),
):
    """Start a new pipeline execution for a user-owned pipeline."""
    pipeline = pipelines_db.get(execution_data.pipeline_id)
    if pipeline is None or pipeline.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {execution_data.pipeline_id}"
        )
    
    orchestration_context = _build_orchestration_context(execution_data)

    # Create execution record
    execution = initialize_execution(
        execution_data.pipeline_id,
        execution_backend=execution_data.execution_backend
    )
    
    # Start execution in background
    background_tasks.add_task(
        execute_pipeline_background,
        execution_data.pipeline_id,
        execution.id,
        execution_data.execution_backend
    )
    
    execution = initialize_execution(execution_data.pipeline_id, context=orchestration_context)

    orchestration_engine = ORCHESTRATION_SCHEMA_TO_CORE[execution_data.orchestration.engine]
    if orchestration_engine == OrchestrationEngine.LOCAL:
        # Start local execution in background
        background_tasks.add_task(
            execute_pipeline_background,
            execution_data.pipeline_id,
            execution.id
        )
    else:
        pipeline = pipelines_db[execution_data.pipeline_id]
        orchestration_request = OrchestrationRequest(
            engine=orchestration_engine,
            execution_id=execution.id,
            pipeline_id=execution.pipeline_id,
            pipeline_name=pipeline.name,
            retry_attempts=execution_data.orchestration.retry_attempts,
            retry_backoff_seconds=execution_data.orchestration.retry_backoff_seconds,
            schedule=execution_data.orchestration.schedule,
            options=execution_data.orchestration.options.copy(),
        )
        orchestration_result = OrchestrationRegistry().get(orchestration_engine).dispatch(orchestration_request)
        execution.add_log(
            None,
            "INFO",
            orchestration_result.message,
            metadata=orchestration_result.metadata,
        )
        execution.context.setdefault("orchestration", {}).update(orchestration_result.metadata)
        execution.status = orchestration_result.status

    execution = initialize_execution(execution_data.pipeline_id, user_id=current_user.user_id)

    background_tasks.add_task(execute_pipeline_background, execution_data.pipeline_id, execution.id)

    return execution


@router.get(
    "",
    response_model=ExecutionListResponse,
    summary="List all executions"
)
async def list_executions(
    pipeline_id: str = None,
    status: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserPrincipal = Depends(get_current_user),
):
    """Get execution list scoped to the authenticated user."""
    all_executions = [e for e in executions_db.values() if e.user_id == current_user.user_id]

    if pipeline_id:
        all_executions = [e for e in all_executions if e.pipeline_id == pipeline_id]
    if status:
        all_executions = [e for e in all_executions if e.status.value == status]

    all_executions.sort(key=lambda x: x.started_at, reverse=True)

    total = len(all_executions)
    executions = all_executions[skip: skip + limit]

    return ExecutionListResponse(executions=executions, total=total)


@router.get(
    "/{execution_id}",
    response_model=ExecutionDetailResponse,
    summary="Get execution details"
)
async def get_execution(execution_id: str, current_user: UserPrincipal = Depends(get_current_user)):
    """Get execution details if it belongs to authenticated user."""
    execution = executions_db.get(execution_id)
    if execution is None or execution.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )

    return execution


@router.get(
    "/{execution_id}/logs",
    response_model=List,
    summary="Get execution logs"
)
async def get_execution_logs(execution_id: str, current_user: UserPrincipal = Depends(get_current_user)):
    """Get logs for a user-owned execution."""
    execution = executions_db.get(execution_id)
    if execution is None or execution.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )

    return execution.logs


@router.delete(
    "/{execution_id}",
    response_model=SuccessResponse,
    summary="Cancel execution"
)
async def cancel_execution(execution_id: str, current_user: UserPrincipal = Depends(get_current_user)):
    """Cancel a running user-owned execution."""
    execution = executions_db.get(execution_id)
    if execution is None or execution.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {execution_id}"
        )

    if execution.status not in [ExecutionStatus.PENDING, ExecutionStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel execution with status: {execution.status.value}"
        )

    from datetime import datetime

    execution.status = ExecutionStatus.CANCELLED
    execution.completed_at = datetime.now()

    return SuccessResponse(message=f"Execution {execution_id} cancelled successfully")
