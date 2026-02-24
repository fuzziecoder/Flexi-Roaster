"""Pipeline orchestration stack metadata routes."""
from fastapi import APIRouter

from backend.api.schemas import OrchestrationOption, OrchestrationStackResponse
from backend.config import settings

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


@router.get("", response_model=OrchestrationStackResponse)
async def get_orchestration_stack() -> OrchestrationStackResponse:
    """Return supported orchestration platforms and current backend choice."""
    return OrchestrationStackResponse(
        orchestration_options=[
            OrchestrationOption(
                name="Apache Airflow",
                category="batch-workflows",
                description="Mature, Python-based DAG orchestration for batch pipelines",
            ),
            OrchestrationOption(
                name="Prefect",
                category="dynamic-workflows",
                description="Easier to use than Airflow with dynamic workflows and cloud execution",
            ),
            OrchestrationOption(
                name="Kubeflow Pipelines",
                category="ml-workflows",
                description="Kubernetes-native machine learning pipeline orchestration",
            ),
            OrchestrationOption(
                name="Dagster",
                category="data-assets-observability",
                description="Strong data asset management and observability for modern data platforms",
            ),
        ],
        current={
            "workflow_orchestration": settings.WORKFLOW_ORCHESTRATION,
            "ml_orchestration": settings.ML_ORCHESTRATION,
            "batch_orchestration": settings.BATCH_ORCHESTRATION,
        },
    )
