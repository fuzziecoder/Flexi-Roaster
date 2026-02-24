"""Data governance integrations for Apache Atlas and Amundsen."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

import httpx

from backend.config import settings


@dataclass
class GovernanceRegistrationResult:
    atlas_status: str
    amundsen_status: str


class GovernanceService:
    """Adapter for catalog sync calls to governance platforms."""

    def __init__(self) -> None:
        self.timeout = 5.0

    async def register_dataset(self, payload: Dict[str, Any]) -> GovernanceRegistrationResult:
        atlas_status = await self._register_atlas(payload)
        amundsen_status = await self._register_amundsen(payload)
        return GovernanceRegistrationResult(
            atlas_status=atlas_status,
            amundsen_status=amundsen_status,
        )

    async def _register_atlas(self, payload: Dict[str, Any]) -> str:
        if not settings.ATLAS_BASE_URL:
            return "disabled"

        atlas_payload = {
            "entity": {
                "typeName": "Dataset",
                "attributes": {
                    "qualifiedName": payload["qualified_name"],
                    "name": payload["name"],
                    "description": payload.get("description", ""),
                    "owner": payload.get("owner", "platform"),
                },
            }
        }

        headers = {"Content-Type": "application/json"}
        if settings.ATLAS_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.ATLAS_API_TOKEN}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{settings.ATLAS_BASE_URL.rstrip('/')}/api/atlas/v2/entity",
                    json=atlas_payload,
                    headers=headers,
                )
                response.raise_for_status()
                return "registered"
        except httpx.HTTPError:
            return "failed"

    async def _register_amundsen(self, payload: Dict[str, Any]) -> str:
        if not settings.AMUNDSEN_BASE_URL:
            return "disabled"

        amundsen_payload = {
            "database": payload.get("database", "flexiroaster"),
            "cluster": payload.get("cluster", "production"),
            "schema": payload.get("schema", "public"),
            "name": payload["name"],
            "description": payload.get("description", ""),
            "owners": [payload.get("owner", "platform")],
            "tags": payload.get("tags", []),
        }

        headers = {"Content-Type": "application/json"}
        if settings.AMUNDSEN_API_TOKEN:
            headers["Authorization"] = f"Bearer {settings.AMUNDSEN_API_TOKEN}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{settings.AMUNDSEN_BASE_URL.rstrip('/')}/api/metadata/v0/register_dataset",
                    json=amundsen_payload,
                    headers=headers,
                )
                response.raise_for_status()
                return "registered"
        except httpx.HTTPError:
            return "failed"
