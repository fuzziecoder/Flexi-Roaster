"""Model serving configuration and deployment capability routes."""
from fastapi import APIRouter

from backend.api.schemas import (
    DeploymentStackResponse,
    ServingOption,
)
from backend.config import settings

router = APIRouter(prefix="/model-serving", tags=["model-serving"])


@router.get("", response_model=DeploymentStackResponse)
async def get_model_serving_stack() -> DeploymentStackResponse:
    """Return supported model serving stacks and current backend deployment choices."""
    return DeploymentStackResponse(
        serving_options=[
            ServingOption(name="FastAPI", category="custom-api", description="Custom Python inference API"),
            ServingOption(name="Flask", category="custom-api", description="Lightweight custom inference API"),
            ServingOption(name="TorchServe", category="framework-specific", description="PyTorch model server"),
            ServingOption(name="TensorFlow Serving", category="framework-specific", description="TensorFlow model server"),
            ServingOption(name="BentoML", category="multi-framework", description="Unified packaging and serving"),
        ],
        containerization="Docker",
        orchestration=["Kubernetes", "KServe", "Seldon Core"],
        current={
            "model_serving": settings.MODEL_SERVING,
            "containerization": settings.CONTAINERIZATION,
            "orchestration": settings.ORCHESTRATION,
        },
    )
