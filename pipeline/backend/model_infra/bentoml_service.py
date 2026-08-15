"""BentoML packaging and model serving helpers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class BentoMLService:
    """Service layer for BentoML model packaging."""

    def build_bento(self, service_import: str, labels: Dict[str, str] | None = None) -> Dict[str, Any]:
        """Package a Bento from a BentoML service import path."""
        try:
            import bentoml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "BentoML is not installed. Install with `pip install bentoml` to package models."
            ) from exc

        bento = bentoml.bentos.build(service=service_import, labels=labels or {})
        return {
            "tag": str(bento.tag),
            "service": service_import,
            "labels": labels or {},
            "path": str(bento.path),
        }

    def list_bentos(self) -> Dict[str, Any]:
        """List locally available bentos."""
        try:
            import bentoml  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "BentoML is not installed. Install with `pip install bentoml` to inspect packaged models."
            ) from exc

        bentos = [str(item.tag) for item in bentoml.bentos.list()]
        return {"bentos": bentos, "count": len(bentos)}


bentoml_service = BentoMLService()
