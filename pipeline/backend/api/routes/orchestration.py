"""Enterprise orchestration endpoints."""
from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel, Field

from core.distributed_execution import execution_dispatcher
from core.enterprise_orchestration import DependencyGraphOptimizer, DynamicDAGGenerator

router = APIRouter(prefix="/orchestration", tags=["orchestration"])


class DynamicDAGRequest(BaseModel):
    metadata: Dict[str, Any]


class DynamicDAGResponse(BaseModel):
    stages: List[Dict[str, Any]] = Field(default_factory=list)
    parallel_groups: List[List[str]] = Field(default_factory=list)
    strategy: str


class AutoScalingRequest(BaseModel):
    active_workers: int = 1


class AutoScalingResponse(BaseModel):
    queue_size: int
    active_workers: int
    recommended_workers: int
    scale_action: str


@router.post("/dag/generate", response_model=DynamicDAGResponse, summary="Generate dynamic DAG from metadata")
async def generate_dynamic_dag(request: DynamicDAGRequest) -> DynamicDAGResponse:
    spec = DynamicDAGGenerator().generate(request.metadata)
    return DynamicDAGResponse(stages=spec.stages, parallel_groups=spec.parallel_groups, strategy=spec.strategy)


@router.post("/dag/optimize", response_model=DynamicDAGResponse, summary="Optimize dependency graph for parallel execution")
async def optimize_dependency_graph(stages: List[Dict[str, Any]]) -> DynamicDAGResponse:
    spec = DependencyGraphOptimizer().optimize(stages)
    return DynamicDAGResponse(stages=spec.stages, parallel_groups=spec.parallel_groups, strategy=spec.strategy)


@router.post("/workers/recommend", response_model=AutoScalingResponse, summary="Recommend worker auto-scaling action")
async def recommend_workers(request: AutoScalingRequest) -> AutoScalingResponse:
    recommendation = execution_dispatcher.autoscaling_recommendation(request.active_workers)
    return AutoScalingResponse(**recommendation)
