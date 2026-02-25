import asyncio

import pytest
from fastapi import BackgroundTasks

from backend.api.routes.executions import create_execution, executions_db
from backend.api.routes.pipelines import pipelines_db
from backend.api.schemas import ExecutionCreate, OrchestrationEngineSchema
from backend.models.pipeline import Pipeline, Stage, StageType


@pytest.fixture(autouse=True)
def clear_stores():
    pipelines_db.clear()
    executions_db.clear()


def _seed_pipeline() -> str:
    pipeline = Pipeline(
        id="pipe-orchestration",
        name="Orchestration Pipeline",
        description="Pipeline for orchestration tests",
        stages=[
            Stage(id="input", name="Input", type=StageType.INPUT, config={"source": "test", "data": [1]}, dependencies=[]),
            Stage(id="output", name="Output", type=StageType.OUTPUT, config={"destination": "sink"}, dependencies=["input"]),
        ],
    )
    pipelines_db[pipeline.id] = pipeline
    return pipeline.id


def test_local_engine_adds_background_task():
    pipeline_id = _seed_pipeline()
    tasks = BackgroundTasks()

    execution = asyncio.run(
        create_execution(
            ExecutionCreate(
                pipeline_id=pipeline_id,
                orchestration={"engine": OrchestrationEngineSchema.LOCAL.value},
            ),
            tasks,
        )
    )

    assert execution.context["orchestration"]["engine"] == "local"
    assert len(tasks.tasks) == 1


def test_temporal_engine_dispatches_without_local_background_task():
    pipeline_id = _seed_pipeline()
    tasks = BackgroundTasks()

    execution = asyncio.run(
        create_execution(
            ExecutionCreate(
                pipeline_id=pipeline_id,
                orchestration={
                    "engine": OrchestrationEngineSchema.TEMPORAL.value,
                    "retry_attempts": 3,
                    "options": {"task_queue": "critical", "workflow_id": "wf-123"},
                },
            ),
            tasks,
        )
    )

    orchestration_context = execution.context["orchestration"]
    assert execution.status.value == "pending"
    assert orchestration_context["provider"] == "temporal"
    assert orchestration_context["task_queue"] == "critical"
    assert orchestration_context["workflow_id"] == "wf-123"
    assert orchestration_context["retry_attempts"] == 3
    assert len(tasks.tasks) == 0


def test_prefect_engine_dispatches_with_schedule_metadata():
    pipeline_id = _seed_pipeline()
    tasks = BackgroundTasks()

    execution = asyncio.run(
        create_execution(
            ExecutionCreate(
                pipeline_id=pipeline_id,
                orchestration={
                    "engine": OrchestrationEngineSchema.PREFECT.value,
                    "schedule": "0 */6 * * *",
                    "options": {"deployment_id": "dep-77", "flow_run_name": "nightly-run"},
                },
            ),
            tasks,
        )
    )

    orchestration_context = execution.context["orchestration"]
    assert orchestration_context["provider"] == "prefect"
    assert orchestration_context["deployment_id"] == "dep-77"
    assert orchestration_context["flow_run_name"] == "nightly-run"
    assert orchestration_context["scheduled_for"] == "0 */6 * * *"
    assert len(tasks.tasks) == 0
