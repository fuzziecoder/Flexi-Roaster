"""
FlexiRoaster Pipeline DAG for Apache Airflow.
Orchestrates pipeline executions via REST API calls to the backend.

This DAG:
- Triggers pipelines via HTTP requests to the FastAPI backend
- Handles retries with exponential backoff
- Reports success/failure status
- Does NOT contain any business logic
"""
import os
from datetime import datetime, timedelta
from typing import Any, Dict

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
import requests


# ===================
# Configuration
# ===================

# Backend configuration from environment or Airflow Variables
BACKEND_URL = os.environ.get(
    "FLEXIROASTER_BACKEND_URL",
    Variable.get("flexiroaster_backend_url", default_var="http://backend:8000")
)
API_PREFIX = os.environ.get(
    "FLEXIROASTER_API_PREFIX",
    Variable.get("flexiroaster_api_prefix", default_var="/api")
)
CALLBACK_SECRET = os.environ.get(
    "FLEXIROASTER_CALLBACK_SECRET",
    Variable.get("flexiroaster_callback_secret", default_var="")
)
TRIGGER_SECRET = os.environ.get(
    "FLEXIROASTER_TRIGGER_SECRET",
    Variable.get("flexiroaster_trigger_secret", default_var="")
)

# Pipeline configuration
PIPELINE_ID = Variable.get("flexiroaster_pipeline_id", default_var="default-pipeline")
PIPELINE_SCHEDULE = Variable.get("flexiroaster_schedule", default_var="0 0 * * *")  # Daily at midnight


# ===================
# Default DAG Arguments
# ===================

default_args = {
    "owner": "flexiroaster",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=30),
    "execution_timeout": timedelta(hours=2),
}


# ===================
# Task Functions
# ===================

def check_backend_health(**context) -> bool:
    """
    Check if the backend is healthy before executing pipeline.
    Raises exception if backend is not available.
    """
    health_url = f"{BACKEND_URL}/health"
    
    try:
        response = requests.get(health_url, timeout=30)
        response.raise_for_status()
        
        health_data = response.json()
        status = health_data.get("status", "unknown")
        
        if status != "healthy":
            raise Exception(f"Backend health check failed: {status}")
        
        print(f"Backend health check passed: {health_data}")
        return True
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Backend health check failed: {e}")


def _trigger_via_compatible_endpoints(pipeline_id: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    """Trigger execution against the available backend contract.

    Tries the newer Airflow-specific endpoint first, then falls back to the
    pipeline backend execution endpoint used by docker-compose stack.
    """
    airflow_trigger_url = f"{BACKEND_URL}{API_PREFIX}/airflow/trigger"
    legacy_execute_url = f"{BACKEND_URL}{API_PREFIX}/executions"

    try:
        response = requests.post(airflow_trigger_url, json=payload, headers=headers, timeout=60)
        if response.status_code != 404:
            response.raise_for_status()
            return response.json()
        print("Airflow trigger endpoint not found; falling back to /executions")
    except requests.exceptions.HTTPError:
        raise

    legacy_payload = {
        "pipeline_id": pipeline_id,
        "variables": payload.get("run_conf", {}),
        "triggered_by": "airflow",
    }
    response = requests.post(legacy_execute_url, json=legacy_payload, headers={"Content-Type": "application/json"}, timeout=60)
    response.raise_for_status()
    return response.json()


def trigger_pipeline_execution(**context) -> Dict[str, Any]:
    """
    Trigger pipeline execution via REST API.
    Returns execution details.
    """
    pipeline_id = context.get("params", {}).get("pipeline_id", PIPELINE_ID)
    execution_url = f"{BACKEND_URL}{API_PREFIX}/airflow/trigger"
    
    # Prepare execution payload
    payload = {
        "pipeline_id": pipeline_id,
        "dag_id": context["dag"].dag_id,
        "dag_run_id": context["run_id"],
        "task_id": context["task"].task_id,
        "run_conf": context.get("params", {}).get("variables", {}),
    }

    headers = {"Content-Type": "application/json"}
    if TRIGGER_SECRET:
        headers["X-Airflow-Trigger-Secret"] = TRIGGER_SECRET

    }
    
    headers = {
        "Content-Type": "application/json",
    }
    if TRIGGER_SECRET:
        headers["X-Airflow-Trigger-Secret"] = TRIGGER_SECRET
    
    try:
        print(f"Triggering pipeline execution: {pipeline_id}")

        result = _trigger_via_compatible_endpoints(pipeline_id, payload, headers)
        print(f"Pipeline execution triggered: {result}")
        
        # Store execution info in XCom for downstream tasks
        context["ti"].xcom_push(key="execution_result", value=result)
        
        return result
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to trigger pipeline: {e}")


def wait_for_execution_completion(**context) -> Dict[str, Any]:
    """
    Poll execution status until completion.
    This is a simplified version - in production, use deferrable operators.
    """
    import time
    
    execution_result = context["ti"].xcom_pull(
        task_ids="trigger_pipeline",
        key="execution_result"
    )
    
    execution_id = execution_result.get("id") or execution_result.get("execution_id")
    execution_id = execution_result.get("id")
    if not execution_id:
        print("No execution ID found, pipeline was started asynchronously")
        return {"status": "accepted"}
    
    status_url = f"{BACKEND_URL}{API_PREFIX}/executions/{execution_id}"
    max_wait_time = 7200  # 2 hours
    poll_interval = 30  # 30 seconds
    elapsed = 0
    
    while elapsed < max_wait_time:
        try:
            response = requests.get(status_url, timeout=30)
            response.raise_for_status()
            
            execution_data = response.json()
            status = execution_data.get("status", "unknown")
            
            print(f"Execution {execution_id} status: {status} "
                  f"({execution_data.get('completed_stages', 0)}/{execution_data.get('total_stages', 0)} stages)")
            
            if status == "completed":
                print(f"Pipeline execution completed successfully")
                return execution_data
            elif status in ["failed", "cancelled", "rolled_back"]:
                raise Exception(f"Pipeline execution {status}: {execution_data.get('error', 'Unknown error')}")
            
            time.sleep(poll_interval)
            elapsed += poll_interval
            
        except requests.exceptions.RequestException as e:
            print(f"Error polling execution status: {e}")
            time.sleep(poll_interval)
            elapsed += poll_interval
    
    raise Exception(f"Execution timed out after {max_wait_time} seconds")


def send_callback(callback_type: str, **context) -> None:
    """
    Send callback notification to backend.
    """
    callback_url = f"{BACKEND_URL}{API_PREFIX}/airflow/callback"
    
    execution_result = context["ti"].xcom_pull(task_ids="trigger_pipeline", key="execution_result") or {}
    execution_id = execution_result.get("id") or execution_result.get("execution_id")
    execution_id = execution_result.get("id")

    if not execution_id:
        print("Skipping callback: no execution ID found in XCom")
        return

    payload = {
        "execution_id": execution_id,
        "dag_id": context["dag"].dag_id,
        "dag_run_id": context["run_id"],
        "task_id": context["task"].task_id,
        "callback_type": callback_type,
        "message": f"Airflow callback from task {context['task'].task_id}",
    }
    if execution_id:
        payload["execution_id"] = execution_id
    
    headers = {"Content-Type": "application/json"}
    if CALLBACK_SECRET:
        headers["X-Airflow-Secret"] = CALLBACK_SECRET
    
    try:
        response = requests.post(
            callback_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        print(f"Callback sent: {callback_type} - {response.status_code}")
    except Exception as e:
        print(f"Failed to send callback: {e}")


def on_success_callback(**context):
    """Success callback handler"""
    send_callback("success", **context)


def on_failure_callback(**context):
    """Failure callback handler"""
    send_callback("failure", **context)


def on_retry_callback(**context):
    """Retry callback handler"""
    send_callback("retry", **context)


# ===================
# DAG Definition
# ===================

with DAG(
    dag_id="flexiroaster_pipeline",
    default_args=default_args,
    description="FlexiRoaster Pipeline Orchestration",
    schedule_interval=PIPELINE_SCHEDULE,
    start_date=days_ago(1),
    catchup=False,
    tags=["flexiroaster", "pipeline", "data"],
    doc_md="""
    # FlexiRoaster Pipeline DAG
    
    This DAG orchestrates pipeline executions through the FlexiRoaster backend.
    
    ## Configuration
    
    Set the following Airflow Variables:
    - `flexiroaster_backend_url`: Backend API URL (default: http://backend:8000)
    - `flexiroaster_pipeline_id`: Pipeline ID to execute
    - `flexiroaster_schedule`: Cron schedule (default: daily at midnight)
    
    ## Flow
    
    1. **Health Check**: Verify backend is available
    2. **Trigger Pipeline**: Start pipeline execution via REST API
    3. **Monitor Execution**: Poll for completion (optional)
    4. **Report Status**: Send callback to backend
    
    ## Error Handling
    
    - Retries: 3 attempts with exponential backoff
    - Timeout: 2 hours per task
    - Callbacks: Sent on success, failure, and retry
    """,
    on_success_callback=on_success_callback,
    on_failure_callback=on_failure_callback,
) as dag:
    
    # Start marker
    start = EmptyOperator(
        task_id="start",
        doc="DAG execution start marker"
    )
    
    # Health check
    health_check = PythonOperator(
        task_id="health_check",
        python_callable=check_backend_health,
        doc="Check if FlexiRoaster backend is healthy"
    )
    
    # Trigger pipeline execution
    trigger_pipeline = PythonOperator(
        task_id="trigger_pipeline",
        python_callable=trigger_pipeline_execution,
        params={"pipeline_id": PIPELINE_ID},
        on_retry_callback=on_retry_callback,
        doc="Trigger pipeline execution via REST API"
    )
    
    # Wait for completion (optional - can be skipped for async execution)
    wait_completion = PythonOperator(
        task_id="wait_for_completion",
        python_callable=wait_for_execution_completion,
        doc="Wait for pipeline execution to complete"
    )
    
    # End marker
    end = EmptyOperator(
        task_id="end",
        doc="DAG execution end marker"
    )
    
    # Task dependencies
    start >> health_check >> trigger_pipeline >> wait_completion >> end


# ===================
# Additional DAGs
# ===================

# DAG for triggering specific pipelines on-demand
with DAG(
    dag_id="flexiroaster_trigger_pipeline",
    default_args=default_args,
    description="Trigger a specific FlexiRoaster pipeline",
    schedule_interval=None,  # Manual trigger only
    start_date=days_ago(1),
    catchup=False,
    tags=["flexiroaster", "pipeline", "trigger"],
    params={
        "pipeline_id": "",
        "variables": {},
    },
    doc_md="""
    # FlexiRoaster Trigger Pipeline DAG
    
    Manually trigger a specific pipeline execution.
    
    ## Parameters
    
    - `pipeline_id`: The ID of the pipeline to execute
    - `variables`: Dictionary of variables to pass to the pipeline
    
    ## Usage
    
    Trigger via Airflow UI or API with the required parameters.
    """,
) as trigger_dag:
    
    start_trigger = EmptyOperator(task_id="start")
    
    health_check_trigger = PythonOperator(
        task_id="health_check",
        python_callable=check_backend_health,
    )
    
    trigger_specific_pipeline = PythonOperator(
        task_id="trigger_pipeline",
        python_callable=trigger_pipeline_execution,
    )
    
    end_trigger = EmptyOperator(task_id="end")
    
    start_trigger >> health_check_trigger >> trigger_specific_pipeline >> end_trigger
