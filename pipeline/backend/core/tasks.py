"""Celery tasks for distributed pipeline execution."""
from celery import Celery

from config import settings
from core.executor import pipeline_executor

celery_app = Celery(
    "flexiroaster_executor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.task_default_queue = settings.CELERY_TASK_QUEUE


@celery_app.task(name="core.tasks.execute_pipeline_task")
def execute_pipeline_task(
    pipeline_id: str,
    pipeline_name: str,
    stages: list,
    variables: dict,
    triggered_by: str,
):
    """Celery entrypoint that runs the async pipeline executor."""
    import asyncio

    async def _run():
        await pipeline_executor.execute_pipeline(
            pipeline_id=pipeline_id,
            pipeline_name=pipeline_name,
            stages=stages,
            variables=variables,
            triggered_by=triggered_by,
        )

    asyncio.run(_run())


__all__ = ["celery_app", "execute_pipeline_task"]
