"""Airflow integration routes for external orchestration callbacks and triggers."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, status

from backend.api.schemas import (
    AirflowCallbackRequest,
    AirflowCallbackTypeSchema,
    AirflowTriggerRequest,
    ExecutionResponse,
    SuccessResponse,
)
from backend.config import settings
from backend.models.pipeline import Execution, ExecutionStatus, LogLevel

from backend.api.routes.executions import (
    execute_pipeline_background,
    executions_db,
    initialize_execution,
)
from backend.api.routes.pipelines import pipelines_db

router = APIRouter(prefix="/airflow", tags=["airflow"])


@router.post(
    "/trigger",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a pipeline run from Airflow",
)
async def trigger_from_airflow(trigger_data: AirflowTriggerRequest, background_tasks: BackgroundTasks):
    """Create an execution from an Airflow DAG/task invocation."""
    if trigger_data.pipeline_id not in pipelines_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pipeline not found: {trigger_data.pipeline_id}",
        )

    execution = initialize_execution(
        trigger_data.pipeline_id,
        context={
            "triggered_by": "airflow",
            "airflow": {
                "dag_id": trigger_data.dag_id,
                "dag_run_id": trigger_data.dag_run_id,
                "task_id": trigger_data.task_id,
                "run_conf": trigger_data.run_conf,
            },
        },
    )
    execution.add_log(
        None,
        LogLevel.INFO,
        f"Execution triggered by Airflow DAG '{trigger_data.dag_id}' run '{trigger_data.dag_run_id}'",
    )

    background_tasks.add_task(
        execute_pipeline_background,
        trigger_data.pipeline_id,
        execution.id,
    )
    return execution


def _validate_execution_lineage(execution: Execution, callback: AirflowCallbackRequest) -> None:
    """Ensure callback dag/run pair matches the execution's original Airflow trigger."""
    airflow_context = execution.context.get("airflow", {})
    expected_dag_id = airflow_context.get("dag_id")
    expected_dag_run_id = airflow_context.get("dag_run_id")

    if expected_dag_id and callback.dag_id != expected_dag_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"DAG mismatch for execution {execution.id}: expected {expected_dag_id}, got {callback.dag_id}",
        )

    if expected_dag_run_id and callback.dag_run_id != expected_dag_run_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"DAG run mismatch for execution {execution.id}: expected {expected_dag_run_id}, got {callback.dag_run_id}",
        )


@router.post(
    "/callback",
    response_model=SuccessResponse,
    summary="Process Airflow callback status updates",
)
async def airflow_callback(
    callback: AirflowCallbackRequest,
    x_airflow_secret: Optional[str] = Header(default=None),
):
    """Update execution status from Airflow callback events."""
    if settings.AIRFLOW_CALLBACK_SECRET and x_airflow_secret != settings.AIRFLOW_CALLBACK_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid callback secret")

    execution = executions_db.get(callback.execution_id)
    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Execution not found: {callback.execution_id}",
        )

    callback_type = callback.callback_type.value
    _validate_execution_lineage(execution, callback)

    if callback_type == AirflowCallbackTypeSchema.SUCCESS.value:
        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.now()
        execution.error = None
    elif callback_type == AirflowCallbackTypeSchema.FAILURE.value:
        execution.status = ExecutionStatus.FAILED
        execution.completed_at = datetime.now()
        execution.error = callback.error or callback.message or "Airflow reported failure"
    elif callback_type == AirflowCallbackTypeSchema.RUNNING.value:
        execution.status = ExecutionStatus.RUNNING
        execution.completed_at = None
    elif callback_type == AirflowCallbackTypeSchema.CANCELLED.value:
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.now()
    elif callback_type == AirflowCallbackTypeSchema.RETRY.value:
        execution.status = ExecutionStatus.PENDING
        execution.completed_at = None

    execution.context.setdefault("triggered_by", "airflow")
    execution.context.setdefault("airflow", {})
    execution.context["airflow"].update(
        {
            "dag_id": callback.dag_id,
            "dag_run_id": callback.dag_run_id,
            "task_id": callback.task_id,
            "last_callback_type": callback_type,
            "last_message": callback.message,
            "last_updated_at": datetime.now().isoformat(),
        }
    )

    log_message = callback.message or f"Airflow callback received: {callback_type}"
    log_level = LogLevel.ERROR if callback_type == AirflowCallbackTypeSchema.FAILURE.value else LogLevel.INFO
    execution.add_log(None, log_level, log_message)

    return SuccessResponse(message=f"Airflow callback processed for execution {callback.execution_id}")
