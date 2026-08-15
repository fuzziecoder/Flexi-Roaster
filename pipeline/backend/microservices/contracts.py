"""Shared contracts for internal microservice communication."""
from __future__ import annotations

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class InternalRequest(BaseModel):
    """Normalized internal request payload for service-to-service calls."""

    action: str = Field(..., description="Operation to execute")
    payload: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = Field(default=None)


class InternalResponse(BaseModel):
    """Normalized internal response payload for service-to-service calls."""

    success: bool = True
    service: str
    protocol: str
    action: str
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
