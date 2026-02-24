"""Feast integration helpers for feature retrieval and materialization."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

from config import settings


@dataclass
class FeastService:
    """Wrapper around Feast's FeatureStore with graceful dependency handling."""

    repo_path: str = "./feature_repo"

    def _load_store(self):
        try:
            from feast import FeatureStore  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "Feast is not installed. Install with `pip install feast` to enable feature-store operations."
            ) from exc

        return FeatureStore(repo_path=self.repo_path)

    def get_online_features(
        self,
        features: List[str],
        entity_rows: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Fetch online features for entity rows from Feast."""
        store = self._load_store()
        response = store.get_online_features(features=features, entity_rows=entity_rows)
        return response.to_dict()

    def materialize(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Materialize offline features into online store for the given time range."""
        store = self._load_store()
        store.materialize(start_date=start_time, end_date=end_time)
        return {
            "status": "success",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "repo_path": self.repo_path,
        }

    def list_feature_views(self) -> Dict[str, Any]:
        """Return all feature view names from the configured Feast repo."""
        store = self._load_store()
        views = [view.name for view in store.list_feature_views()]
        return {"feature_views": views, "count": len(views), "repo_path": self.repo_path}


feast_service = FeastService(repo_path=settings.FEAST_REPO_PATH)
