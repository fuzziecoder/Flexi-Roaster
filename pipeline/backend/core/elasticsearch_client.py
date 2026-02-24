"""
Elasticsearch client utilities for FlexiRoaster.
Handles log indexing and search/filter operations for execution analytics.
"""
import logging
from typing import Optional, Dict, Any, List

from elasticsearch import AsyncElasticsearch

from config import settings

logger = logging.getLogger(__name__)


class ElasticsearchManager:
    """Manages Elasticsearch lifecycle and execution log indexing."""

    def __init__(self) -> None:
        self._client: Optional[AsyncElasticsearch] = None
        self._available: bool = False

    @property
    def is_available(self) -> bool:
        return self._available

    async def initialize(self) -> bool:
        if not settings.ELASTICSEARCH_ENABLED:
            logger.info("Elasticsearch disabled via configuration")
            self._available = False
            return False

        try:
            auth = None
            if settings.ELASTICSEARCH_USERNAME and settings.ELASTICSEARCH_PASSWORD:
                auth = (settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD)

            self._client = AsyncElasticsearch(
                hosts=[settings.ELASTICSEARCH_URL],
                basic_auth=auth,
                verify_certs=settings.ELASTICSEARCH_VERIFY_CERTS,
                request_timeout=settings.ELASTICSEARCH_REQUEST_TIMEOUT,
            )

            await self._client.ping()
            await self.ensure_index()

            self._available = True
            logger.info("Elasticsearch initialized")
            return True
        except Exception as e:
            logger.warning(f"Elasticsearch unavailable, continuing without indexing: {e}")
            self._available = False
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.close()
        self._available = False

    async def ensure_index(self) -> None:
        if not self._client:
            return

        index_name = settings.ELASTICSEARCH_LOGS_INDEX
        exists = await self._client.indices.exists(index=index_name)
        if exists:
            return

        await self._client.indices.create(
            index=index_name,
            mappings={
                "properties": {
                    "timestamp": {"type": "date"},
                    "execution_id": {"type": "keyword"},
                    "pipeline_id": {"type": "keyword"},
                    "stage_id": {"type": "keyword"},
                    "level": {"type": "keyword"},
                    "message": {"type": "text"},
                    "metadata": {"type": "object", "enabled": True},
                }
            },
        )

    async def health_check(self) -> Dict[str, Any]:
        if not settings.ELASTICSEARCH_ENABLED:
            return {"status": "disabled"}

        if not self._client:
            return {"status": "disconnected"}

        try:
            health = await self._client.cluster.health()
            return {
                "status": "healthy",
                "cluster_status": health.get("status"),
                "number_of_nodes": health.get("number_of_nodes"),
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def index_execution_log(self, document: Dict[str, Any]) -> bool:
        if not self._available or not self._client:
            return False

        try:
            await self._client.index(index=settings.ELASTICSEARCH_LOGS_INDEX, document=document)
            return True
        except Exception as e:
            logger.warning(f"Failed to index log in Elasticsearch: {e}")
            return False

    async def search_logs(
        self,
        query: str,
        pipeline_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        levels: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if not self._available or not self._client:
            return []

        filters = []
        if pipeline_id:
            filters.append({"term": {"pipeline_id": pipeline_id}})
        if execution_id:
            filters.append({"term": {"execution_id": execution_id}})
        if levels:
            filters.append({"terms": {"level": levels}})

        body: Dict[str, Any] = {
            "size": limit,
            "query": {
                "bool": {
                    "must": [{"multi_match": {"query": query, "fields": ["message", "metadata.*"]}}],
                    "filter": filters,
                }
            },
            "sort": [{"timestamp": {"order": "desc"}}],
        }

        response = await self._client.search(index=settings.ELASTICSEARCH_LOGS_INDEX, body=body)
        return [hit.get("_source", {}) for hit in response.get("hits", {}).get("hits", [])]


elasticsearch_manager = ElasticsearchManager()
