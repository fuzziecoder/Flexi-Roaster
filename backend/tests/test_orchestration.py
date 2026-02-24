import asyncio

from backend.api.routes.orchestration import get_orchestration_stack
from backend.config import settings


def test_orchestration_stack_includes_requested_platforms():
    response = asyncio.run(get_orchestration_stack())

    names = {item.name for item in response.orchestration_options}
    assert {"Apache Airflow", "Prefect", "Kubeflow Pipelines", "Dagster"}.issubset(names)


def test_orchestration_stack_includes_current_configuration():
    response = asyncio.run(get_orchestration_stack())

    assert response.current["workflow_orchestration"] == settings.WORKFLOW_ORCHESTRATION
    assert response.current["ml_orchestration"] == settings.ML_ORCHESTRATION
    assert response.current["batch_orchestration"] == settings.BATCH_ORCHESTRATION
