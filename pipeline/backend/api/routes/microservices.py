"""Microservice architecture routes."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

from microservices import MicroserviceOrchestrator

router = APIRouter(prefix="/microservices", tags=["microservices"])
orchestrator = MicroserviceOrchestrator()


class InternalCallRequest(BaseModel):
    service: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    protocol: str = "rest"
    correlation_id: Optional[str] = None


@router.get("/architecture")
async def get_architecture() -> Dict[str, List[Dict[str, Any]]]:
    """Return the microservice topology and communication endpoints."""
    return {"services": orchestrator.architecture()}


@router.post("/call")
async def call_internal_service(request: InternalCallRequest) -> Dict[str, Any]:
    """Proxy an internal service call using REST or gRPC transport."""
    try:
        response = await orchestrator.call(
            service_name=request.service,
            action=request.action,
            payload=request.payload,
            protocol=request.protocol,
            correlation_id=request.correlation_id,
        )
        return response.model_dump()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
