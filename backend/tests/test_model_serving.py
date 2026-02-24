import asyncio

from backend.api.routes.model_serving import get_model_serving_stack
from backend.config import settings


def test_model_serving_stack_response_contains_required_options():
    response = asyncio.run(get_model_serving_stack())

    names = {item.name for item in response.serving_options}
    assert {"FastAPI", "Flask", "TorchServe", "TensorFlow Serving", "BentoML"}.issubset(names)
    assert response.containerization == "Docker"
    assert response.orchestration == ["Kubernetes", "KServe", "Seldon Core"]


def test_model_serving_stack_includes_current_backend_configuration():
    response = asyncio.run(get_model_serving_stack())

    assert response.current["model_serving"] == settings.MODEL_SERVING
    assert response.current["containerization"] == settings.CONTAINERIZATION
    assert response.current["orchestration"] == settings.ORCHESTRATION
