"""Advanced orchestration stack endpoints."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from api.security import AuthContext, require_roles
from core.modern_stack import ModernOrchestrationStack

router = APIRouter(prefix="/advanced-stack", tags=["advanced-stack"])
stack = ModernOrchestrationStack()


class StackExecutionRequest(BaseModel):
    pipeline_id: str = Field(..., description="Pipeline identifier to execute")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Execution payload")


@router.get("/architecture")
async def get_stack_architecture(
    _: AuthContext = Depends(require_roles("admin", "operator", "viewer")),
) -> Dict[str, Any]:
    """Return current high-end orchestration stack architecture."""
    return stack.architecture()


@router.post("/executions")
async def submit_stack_execution(
    request: StackExecutionRequest,
    _: AuthContext = Depends(require_roles("admin", "operator")),
) -> Dict[str, Any]:
    """Submit an execution envelope for orchestration connectors."""
    return stack.submit_execution(request.pipeline_id, request.payload)
