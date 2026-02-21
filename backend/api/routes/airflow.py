"""Airflow integration routes for external orchestration callbacks and triggers."""
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, status

from backend.api.schemas import (
    AirflowCallbackRequest,
    AirflowTriggerRequest,
    ExecutionResponse,
    SuccessResponse,
)
from backend.config import settings
from backend.models.pipeline import ExecutionStatus, LogLevel

from backend.api.routes.pipelines import pipelines_db
from backend.api.routes.executions import (
    execute_pipeline_background,
    executions_db,
    initialize_execution,
)

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


@router.post(
    "/callback",
    response_model=SuccessResponse,
    summary="Process Airflow callback status updates",
)
async def airflow_callback(
    callback: AirflowCallbackRequest,
    x_airflow_secret: str = Header(default=None),
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

    callback_type = callback.callback_type.lower()
    if callback_type == "success":
        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.now()
    elif callback_type == "failure":
        execution.status = ExecutionStatus.FAILED
        execution.completed_at = datetime.now()
        execution.error = callback.error or callback.message or "Airflow reported failure"
    elif callback_type == "running":
        execution.status = ExecutionStatus.RUNNING
    elif callback_type == "cancelled":
        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.now()
    elif callback_type == "retry":
        execution.status = ExecutionStatus.PENDING
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported callback_type: {callback.callback_type}",
        )

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
    log_level = LogLevel.ERROR if callback_type == "failure" else LogLevel.INFO
    execution.add_log(None, log_level, log_message)

    return SuccessResponse(message=f"Airflow callback processed for execution {callback.execution_id}")
