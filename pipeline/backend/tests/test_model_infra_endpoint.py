import asyncio
import importlib.util
from pathlib import Path

import pytest
from fastapi import HTTPException

MODULE_PATH = Path(__file__).resolve().parents[1] / "api" / "routes" / "model_infra.py"
SPEC = importlib.util.spec_from_file_location("model_infra_route_module", MODULE_PATH)
model_infra = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(model_infra)


class StubFeastService:
    def list_feature_views(self):
        return {"feature_views": ["pipeline_features"], "count": 1}

    def get_online_features(self, features, entity_rows):
        return {"features": features, "rows": entity_rows}

    def materialize(self, start_time, end_time):
        return {"status": "success", "start": start_time.isoformat(), "end": end_time.isoformat()}


class StubBentoService:
    def list_bentos(self):
        return {"bentos": ["fraud_model:latest"], "count": 1}

    def build_bento(self, service_import, labels):
        return {"tag": "fraud_model:abc123", "service": service_import, "labels": labels}


class StubKubeflowService:
    def compile_pipeline(self, module_path, function_name, output_path):
        return {"status": "compiled", "output_path": output_path, "pipeline_function": function_name}

    def submit_run(self, pipeline_package_path, run_name, experiment_name):
        return {"status": "submitted", "run_name": run_name, "experiment_name": experiment_name}


def test_model_infra_happy_path(monkeypatch):
    monkeypatch.setattr(model_infra, "feast_service", StubFeastService())
    monkeypatch.setattr(model_infra, "bentoml_service", StubBentoService())
    monkeypatch.setattr(model_infra, "kubeflow_service", StubKubeflowService())

    overview = asyncio.run(model_infra.infrastructure_overview())
    views = asyncio.run(model_infra.list_feature_views())
    bento_list = asyncio.run(model_infra.list_bentos())

    assert overview["model_serving"] == "FastAPI + BentoML"
    assert views["count"] == 1
    assert bento_list["count"] == 1


def test_feature_endpoint_raises_http_exception_when_service_unavailable(monkeypatch):
    class FailingFeastService:
        def list_feature_views(self):
            raise RuntimeError("Feast unavailable")

    monkeypatch.setattr(model_infra, "feast_service", FailingFeastService())

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(model_infra.list_feature_views())

    assert exc_info.value.status_code == 503
    assert "Feast unavailable" in exc_info.value.detail
