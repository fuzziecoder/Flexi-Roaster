import asyncio

import pytest
from fastapi import BackgroundTasks, HTTPException

from backend.api.routes.airflow import airflow_callback, trigger_from_airflow
from backend.api.routes.executions import executions_db
from backend.api.routes.pipelines import pipelines_db
from backend.api.schemas import AirflowCallbackRequest, AirflowTriggerRequest
from backend.config import settings
from backend.models.pipeline import Pipeline, Stage, StageType


@pytest.fixture(autouse=True)
def clear_stores():
    pipelines_db.clear()
    executions_db.clear()


def _seed_pipeline() -> str:
    pipeline = Pipeline(
        id="pipe-airflow",
        name="Airflow Pipeline",
        description="Integration test pipeline",
        stages=[
            Stage(id="s1", name="Input", type=StageType.INPUT, config={"source": "test", "data": [1]}, dependencies=[]),
            Stage(id="s2", name="Output", type=StageType.OUTPUT, config={"destination": "sink"}, dependencies=["s1"]),
        ],
    )
    pipelines_db[pipeline.id] = pipeline
    return pipeline.id


def test_airflow_trigger_seeds_context_and_queues_background_tasks():
    pipeline_id = _seed_pipeline()
    tasks = BackgroundTasks()

    execution = asyncio.run(
        trigger_from_airflow(
            AirflowTriggerRequest(pipeline_id=pipeline_id, dag_id="dag-a", dag_run_id="run-a", task_id="task-a"),
            tasks,
        )
    )

    assert execution.context["triggered_by"] == "airflow"
    assert execution.context["airflow"]["dag_id"] == "dag-a"
    assert len(tasks.tasks) == 1


def test_airflow_callback_rejects_mismatched_dag_run():
    pipeline_id = _seed_pipeline()
    execution = asyncio.run(
        trigger_from_airflow(
            AirflowTriggerRequest(pipeline_id=pipeline_id, dag_id="dag-a", dag_run_id="run-a"),
            BackgroundTasks(),
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            airflow_callback(
                AirflowCallbackRequest(
                    execution_id=execution.id,
                    callback_type="success",
                    dag_id="dag-a",
                    dag_run_id="run-b",
                ),
                None,
            )
        )

    assert exc_info.value.status_code == 409


def test_airflow_callback_enforces_secret_when_configured():
    pipeline_id = _seed_pipeline()
    execution = asyncio.run(
        trigger_from_airflow(
            AirflowTriggerRequest(pipeline_id=pipeline_id, dag_id="dag-a", dag_run_id="run-a"),
            BackgroundTasks(),
        )
    )

    original_secret = settings.AIRFLOW_CALLBACK_SECRET
    settings.AIRFLOW_CALLBACK_SECRET = "expected-secret"
    try:
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                airflow_callback(
                    AirflowCallbackRequest(
                        execution_id=execution.id,
                        callback_type="running",
                        dag_id="dag-a",
                        dag_run_id="run-a",
                    ),
                    "wrong-secret",
                )
            )

        assert exc_info.value.status_code == 401
    finally:
        settings.AIRFLOW_CALLBACK_SECRET = original_secret
