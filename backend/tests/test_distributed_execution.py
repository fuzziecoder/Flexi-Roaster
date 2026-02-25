import asyncio

from fastapi import BackgroundTasks

from backend.api.routes.executions import create_execution, execute_pipeline_background, executions_db
from backend.api.routes.pipelines import create_pipeline, pipelines_db
from backend.api.schemas import ExecutionCreate, PipelineCreate, StageCreate, StageTypeSchema
from backend.core.distributed_executor import DistributedExecutionDispatcher
from backend.models.pipeline import ExecutionStatus


def _build_pipeline():
    pipelines_db.clear()
    executions_db.clear()
    return asyncio.run(
        create_pipeline(
            PipelineCreate(
                name="distributed-pipeline",
                description="pipeline for distributed testing",
                stages=[
                    StageCreate(id="in", name="Input", type=StageTypeSchema.INPUT, config={"source": "x", "data": [1, 2]}),
                    StageCreate(
                        id="out",
                        name="Output",
                        type=StageTypeSchema.OUTPUT,
                        config={"destination": "console"},
                        dependencies=["in"],
                    ),
                ],
            )
        )
    )


def test_dispatcher_falls_back_to_local_for_unknown_backend():
    pipeline = _build_pipeline()

    dispatcher = DistributedExecutionDispatcher()
    result = dispatcher.run(pipeline, backend_override="spark")

    assert result.backend_used == "local"
    assert result.execution.status == ExecutionStatus.COMPLETED


def test_create_execution_tracks_requested_backend_and_backend_used():
    pipeline = _build_pipeline()

    execution = asyncio.run(
        create_execution(
            ExecutionCreate(pipeline_id=pipeline.id, execution_backend="celery"),
            BackgroundTasks(),
        )
    )

    assert execution.context["requested_execution_backend"] == "celery"

    asyncio.run(execute_pipeline_background(pipeline.id, execution.id, "celery"))
    stored = executions_db[execution.id]

    assert stored.context["requested_execution_backend"] == "celery"
    assert stored.context["distributed_execution"]["backend_used"] == "local"
