"""
Redis-backed services for sessions, rate limiting, and background job brokering.
"""
import json
from datetime import datetime
from typing import Any, Dict, Optional

from config import settings
from core.redis_state import redis_state_manager


class RedisServiceLayer:
    SESSION_KEY = "flexiroaster:session:{session_id}"
    RATE_LIMIT_KEY = "flexiroaster:ratelimit:{identifier}:{window}"

    async def set_session(self, session_id: str, payload: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        if not redis_state_manager.is_available:
            return False

        key = self.SESSION_KEY.format(session_id=session_id)
        ttl_value = ttl or settings.REDIS_SESSION_TTL
        await redis_state_manager.client.set(key, json.dumps(payload), ex=ttl_value)
        return True

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        if not redis_state_manager.is_available:
            return None

        key = self.SESSION_KEY.format(session_id=session_id)
        value = await redis_state_manager.client.get(key)
        if not value:
            return None
        return json.loads(value)

    async def check_rate_limit(
        self,
        identifier: str,
        max_requests: Optional[int] = None,
        window_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not redis_state_manager.is_available:
            return {"allowed": True, "remaining": -1, "window_seconds": window_seconds or settings.REDIS_RATE_LIMIT_WINDOW_SECONDS}

        limit = max_requests or settings.REDIS_RATE_LIMIT_MAX_REQUESTS
        window = window_seconds or settings.REDIS_RATE_LIMIT_WINDOW_SECONDS
        current_window = int(datetime.now().timestamp() // window)

        key = self.RATE_LIMIT_KEY.format(identifier=identifier, window=current_window)
        current_count = await redis_state_manager.client.incr(key)
        if current_count == 1:
            await redis_state_manager.client.expire(key, window)

        remaining = max(limit - current_count, 0)
        return {
            "allowed": current_count <= limit,
            "remaining": remaining,
            "window_seconds": window,
            "used": current_count,
            "limit": limit,
        }

    async def enqueue_job(self, payload: Dict[str, Any], queue_key: Optional[str] = None) -> bool:
        if not redis_state_manager.is_available:
            return False

        key = queue_key or settings.REDIS_JOB_QUEUE_KEY
        await redis_state_manager.client.lpush(key, json.dumps(payload))
        return True

    async def dequeue_job(self, queue_key: Optional[str] = None, timeout: Optional[int] = None) -> Optional[Dict[str, Any]]:
        if not redis_state_manager.is_available:
            return None

        key = queue_key or settings.REDIS_JOB_QUEUE_KEY
        wait_timeout = timeout or settings.REDIS_JOB_QUEUE_TIMEOUT
        result = await redis_state_manager.client.brpop(key, timeout=wait_timeout)
        if not result:
            return None

        _, payload = result
        return json.loads(payload)


redis_service_layer = RedisServiceLayer()
