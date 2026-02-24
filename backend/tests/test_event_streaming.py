import asyncio

from fastapi import BackgroundTasks

from backend.api.routes.executions import create_execution, execute_pipeline_background, executions_db
from backend.api.routes.pipelines import create_pipeline, pipelines_db
from backend.api.schemas import ExecutionCreate, PipelineCreate, StageCreate, StageTypeSchema


class _StubPublisher:
    def __init__(self):
        self.events = []

    def publish(self, topic, key, payload):
        self.events.append({"topic": topic, "key": key, "payload": payload})


def _seed_pipeline_and_stub(monkeypatch):
    pipelines_db.clear()
    executions_db.clear()

    stub = _StubPublisher()
    monkeypatch.setattr("backend.api.routes.pipelines.get_event_publisher", lambda: stub)
    monkeypatch.setattr("backend.api.routes.executions.get_event_publisher", lambda: stub)

    pipeline = asyncio.run(
        create_pipeline(
            PipelineCreate(
                name="event-pipeline",
                description="pipeline for events",
                stages=[
                    StageCreate(id="s1", name="Input", type=StageTypeSchema.INPUT, config={"source": "x", "data": [1]}),
                    StageCreate(
                        id="s2",
                        name="Output",
                        type=StageTypeSchema.OUTPUT,
                        config={"destination": "console"},
                        dependencies=["s1"],
                    ),
                ],
            )
        )
    )
    return pipeline, stub


def test_emits_pipeline_created_event(monkeypatch):
    _, stub = _seed_pipeline_and_stub(monkeypatch)

    topics = [event["topic"] for event in stub.events]
    assert "pipeline.created" in topics


def test_emits_execution_started_and_completed_events(monkeypatch):
    pipeline, stub = _seed_pipeline_and_stub(monkeypatch)

    execution = asyncio.run(create_execution(ExecutionCreate(pipeline_id=pipeline.id), BackgroundTasks()))
    asyncio.run(execute_pipeline_background(pipeline.id, execution.id))

    topics = [event["topic"] for event in stub.events]
    assert "execution.started" in topics
    assert "execution.completed" in topics
