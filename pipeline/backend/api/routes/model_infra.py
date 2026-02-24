"""Endpoints for model serving, feature store, and ML orchestration infrastructure."""
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import settings
from model_infra import bentoml_service, feast_service, kubeflow_service

router = APIRouter(prefix="/model-infra", tags=["model-infra"])


class OnlineFeaturesRequest(BaseModel):
    features: List[str]
    entity_rows: List[Dict[str, Any]]


class MaterializeRequest(BaseModel):
    start_time: datetime
    end_time: datetime


class BuildBentoRequest(BaseModel):
    service_import: str = Field(..., examples=["service:svc"])
    labels: Dict[str, str] = Field(default_factory=dict)


class CompileKubeflowRequest(BaseModel):
    module_path: str
    function_name: str
    output_path: str


class SubmitKubeflowRunRequest(BaseModel):
    pipeline_package_path: str
    run_name: str
    experiment_name: str


@router.get("/overview", response_model=Dict[str, Any])
async def infrastructure_overview():
    return {
        "model_serving": "FastAPI + BentoML",
        "feature_store": "Feast",
        "orchestration": "Kubeflow Pipelines",
        "api_prefix": settings.API_PREFIX,
    }


@router.get("/features/views", response_model=Dict[str, Any])
async def list_feature_views():
    try:
        return feast_service.list_feature_views()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/features/online", response_model=Dict[str, Any])
async def fetch_online_features(payload: OnlineFeaturesRequest):
    try:
        return feast_service.get_online_features(payload.features, payload.entity_rows)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/features/materialize", response_model=Dict[str, Any])
async def materialize_features(payload: MaterializeRequest):
    try:
        return feast_service.materialize(payload.start_time, payload.end_time)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/bentoml/bentos", response_model=Dict[str, Any])
async def list_bentos():
    try:
        return bentoml_service.list_bentos()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/bentoml/build", response_model=Dict[str, Any])
async def build_bento(payload: BuildBentoRequest):
    try:
        return bentoml_service.build_bento(payload.service_import, payload.labels)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/kubeflow/compile", response_model=Dict[str, Any])
async def compile_kubeflow_pipeline(payload: CompileKubeflowRequest):
    try:
        return kubeflow_service.compile_pipeline(
            module_path=payload.module_path,
            function_name=payload.function_name,
            output_path=payload.output_path,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/kubeflow/submit", response_model=Dict[str, Any])
async def submit_kubeflow_pipeline(payload: SubmitKubeflowRunRequest):
    try:
        return kubeflow_service.submit_run(
            pipeline_package_path=payload.pipeline_package_path,
            run_name=payload.run_name,
            experiment_name=payload.experiment_name,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
