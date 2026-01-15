"""
Redis State Manager for FlexiRoaster Pipeline Automation.
Handles distributed locks, execution state, retry counters, and heartbeat monitoring.
"""
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager
from enum import Enum

import redis.asyncio as redis
from redis.asyncio.lock import Lock
from redis.exceptions import RedisError, LockError, ConnectionError as RedisConnectionError

from config import settings

logger = logging.getLogger(__name__)


class RedisKeys:
    """Redis key patterns for FlexiRoaster"""
    
    # Execution locks
    EXECUTION_LOCK = "flexiroaster:lock:execution:{execution_id}"
    PIPELINE_LOCK = "flexiroaster:lock:pipeline:{pipeline_id}"
    
    # Execution state
    EXECUTION_STATE = "flexiroaster:state:execution:{execution_id}"
    STAGE_STATE = "flexiroaster:state:stage:{execution_id}:{stage_id}"
    
    # Retry counters
    RETRY_COUNTER = "flexiroaster:retry:{execution_id}:{stage_id}"
    
    # Heartbeat
    HEARTBEAT = "flexiroaster:heartbeat:{execution_id}"
    
    # Running executions set
    RUNNING_EXECUTIONS = "flexiroaster:running_executions"
    
    # Cache
    PIPELINE_CACHE = "flexiroaster:cache:pipeline:{pipeline_id}"
    STATS_CACHE = "flexiroaster:cache:stats:{pipeline_id}"


class ExecutionState(str, Enum):
    """Execution states stored in Redis"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class RedisStateManager:
    """
    Manages execution state, locks, and caching using Redis.
    Provides fallback mechanisms when Redis is unavailable.
    """
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._available: bool = False
        self._fallback_mode: bool = False
        self._local_locks: Dict[str, bool] = {}  # Fallback locks
        
    async def initialize(self) -> bool:
        """Initialize Redis connection pool"""
        try:
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                retry_on_timeout=settings.REDIS_RETRY_ON_TIMEOUT,
                decode_responses=settings.REDIS_DECODE_RESPONSES
            )
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            self._available = True
            self._fallback_mode = False
            logger.info("Redis connection established successfully")
            return True
            
        except RedisConnectionError as e:
            logger.warning(f"Redis connection failed, using fallback mode: {e}")
            self._available = False
            self._fallback_mode = True
            return False
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            self._available = False
            self._fallback_mode = True
            return False
    
    async def close(self) -> None:
        """Close Redis connections"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        logger.info("Redis connections closed")
    
    @property
    def is_available(self) -> bool:
        """Check if Redis is available"""
        return self._available
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Redis health status"""
        try:
            if not self._client:
                return {"status": "disconnected", "fallback_mode": True}
            
            start = datetime.now()
            await self._client.ping()
            latency = (datetime.now() - start).total_seconds() * 1000
            
            info = await self._client.info("memory")
            
            return {
                "status": "healthy",
                "latency_ms": round(latency, 2),
                "used_memory": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "fallback_mode": False
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "fallback_mode": True
            }
    
    # ==================
    # Distributed Locks
    # ==================
    
    @asynccontextmanager
    async def acquire_execution_lock(
        self,
        execution_id: str,
        timeout: int = None
    ):
        """
        Acquire a distributed lock for an execution.
        Falls back to local lock if Redis is unavailable.
        """
        timeout = timeout or settings.EXECUTION_LOCK_TTL
        lock_key = RedisKeys.EXECUTION_LOCK.format(execution_id=execution_id)
        lock = None
        
        try:
            if self._available and self._client:
                lock = self._client.lock(
                    lock_key,
                    timeout=timeout,
                    blocking_timeout=settings.EXECUTION_LOCK_RETRY_DELAY * settings.EXECUTION_LOCK_MAX_RETRIES
                )
                acquired = await lock.acquire()
                if not acquired:
                    raise LockError(f"Could not acquire lock for execution {execution_id}")
                logger.debug(f"Acquired Redis lock for execution {execution_id}")
            else:
                # Fallback to local lock
                if lock_key in self._local_locks:
                    raise LockError(f"Local lock already held for execution {execution_id}")
                self._local_locks[lock_key] = True
                logger.debug(f"Acquired local lock for execution {execution_id}")
            
            yield
            
        finally:
            try:
                if lock:
                    await lock.release()
                    logger.debug(f"Released Redis lock for execution {execution_id}")
                elif lock_key in self._local_locks:
                    del self._local_locks[lock_key]
                    logger.debug(f"Released local lock for execution {execution_id}")
            except Exception as e:
                logger.warning(f"Error releasing lock: {e}")
    
    async def is_execution_locked(self, execution_id: str) -> bool:
        """Check if an execution is currently locked"""
        lock_key = RedisKeys.EXECUTION_LOCK.format(execution_id=execution_id)
        
        if self._available and self._client:
            try:
                return await self._client.exists(lock_key) > 0
            except RedisError:
                pass
        
        return lock_key in self._local_locks
    
    async def prevent_duplicate_run(self, pipeline_id: str) -> bool:
        """
        Prevent duplicate pipeline runs.
        Returns True if a run is already in progress.
        """
        lock_key = RedisKeys.PIPELINE_LOCK.format(pipeline_id=pipeline_id)
        
        if self._available and self._client:
            try:
                # Try to set a lock that expires after execution timeout
                result = await self._client.set(
                    lock_key,
                    datetime.now().isoformat(),
                    nx=True,  # Only set if not exists
                    ex=settings.EXECUTOR_DEFAULT_TIMEOUT
                )
                return result is None  # None means key already exists
            except RedisError as e:
                logger.warning(f"Redis error checking duplicate run: {e}")
        
        # Fallback: check local state
        return lock_key in self._local_locks
    
    async def release_pipeline_lock(self, pipeline_id: str) -> None:
        """Release pipeline lock after execution completes"""
        lock_key = RedisKeys.PIPELINE_LOCK.format(pipeline_id=pipeline_id)
        
        if self._available and self._client:
            try:
                await self._client.delete(lock_key)
            except RedisError as e:
                logger.warning(f"Redis error releasing pipeline lock: {e}")
        
        if lock_key in self._local_locks:
            del self._local_locks[lock_key]
    
    # ==================
    # Execution State
    # ==================
    
    async def set_execution_state(
        self,
        execution_id: str,
        state: ExecutionState,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """Set execution state in Redis"""
        key = RedisKeys.EXECUTION_STATE.format(execution_id=execution_id)
        data = {
            "state": state.value,
            "updated_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if self._available and self._client:
            try:
                await self._client.set(key, json.dumps(data), ex=ttl)
                
                # Track running executions
                if state == ExecutionState.RUNNING:
                    await self._client.sadd(RedisKeys.RUNNING_EXECUTIONS, execution_id)
                elif state in [ExecutionState.COMPLETED, ExecutionState.FAILED, 
                               ExecutionState.CANCELLED, ExecutionState.ROLLED_BACK]:
                    await self._client.srem(RedisKeys.RUNNING_EXECUTIONS, execution_id)
                
                return True
            except RedisError as e:
                logger.warning(f"Redis error setting execution state: {e}")
        
        return False
    
    async def get_execution_state(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution state from Redis"""
        key = RedisKeys.EXECUTION_STATE.format(execution_id=execution_id)
        
        if self._available and self._client:
            try:
                data = await self._client.get(key)
                if data:
                    return json.loads(data)
            except RedisError as e:
                logger.warning(f"Redis error getting execution state: {e}")
        
        return None
    
    async def set_stage_state(
        self,
        execution_id: str,
        stage_id: str,
        state: str,
        output: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ) -> bool:
        """Set stage execution state"""
        key = RedisKeys.STAGE_STATE.format(
            execution_id=execution_id,
            stage_id=stage_id
        )
        data = {
            "state": state,
            "updated_at": datetime.now().isoformat(),
            "output": output,
            "error": error
        }
        
        if self._available and self._client:
            try:
                await self._client.set(key, json.dumps(data), ex=86400)
                return True
            except RedisError as e:
                logger.warning(f"Redis error setting stage state: {e}")
        
        return False
    
    async def get_running_executions(self) -> List[str]:
        """Get list of currently running execution IDs"""
        if self._available and self._client:
            try:
                return list(await self._client.smembers(RedisKeys.RUNNING_EXECUTIONS))
            except RedisError as e:
                logger.warning(f"Redis error getting running executions: {e}")
        
        return []
    
    # ==================
    # Retry Counters
    # ==================
    
    async def increment_retry_counter(
        self,
        execution_id: str,
        stage_id: str
    ) -> int:
        """Increment and return retry counter for a stage"""
        key = RedisKeys.RETRY_COUNTER.format(
            execution_id=execution_id,
            stage_id=stage_id
        )
        
        if self._available and self._client:
            try:
                count = await self._client.incr(key)
                await self._client.expire(key, 86400)  # 24 hour TTL
                return count
            except RedisError as e:
                logger.warning(f"Redis error incrementing retry counter: {e}")
        
        # Fallback: no retry tracking
        return 1
    
    async def get_retry_count(self, execution_id: str, stage_id: str) -> int:
        """Get current retry count for a stage"""
        key = RedisKeys.RETRY_COUNTER.format(
            execution_id=execution_id,
            stage_id=stage_id
        )
        
        if self._available and self._client:
            try:
                count = await self._client.get(key)
                return int(count) if count else 0
            except RedisError as e:
                logger.warning(f"Redis error getting retry count: {e}")
        
        return 0
    
    async def reset_retry_counter(self, execution_id: str, stage_id: str) -> None:
        """Reset retry counter for a stage"""
        key = RedisKeys.RETRY_COUNTER.format(
            execution_id=execution_id,
            stage_id=stage_id
        )
        
        if self._available and self._client:
            try:
                await self._client.delete(key)
            except RedisError as e:
                logger.warning(f"Redis error resetting retry counter: {e}")
    
    # ==================
    # Heartbeat Monitoring
    # ==================
    
    async def send_heartbeat(self, execution_id: str) -> bool:
        """Send heartbeat for an execution"""
        key = RedisKeys.HEARTBEAT.format(execution_id=execution_id)
        
        if self._available and self._client:
            try:
                await self._client.set(
                    key,
                    datetime.now().isoformat(),
                    ex=settings.HEARTBEAT_TTL
                )
                return True
            except RedisError as e:
                logger.warning(f"Redis error sending heartbeat: {e}")
        
        return False
    
    async def check_heartbeat(self, execution_id: str) -> Optional[datetime]:
        """Check last heartbeat for an execution"""
        key = RedisKeys.HEARTBEAT.format(execution_id=execution_id)
        
        if self._available and self._client:
            try:
                timestamp = await self._client.get(key)
                if timestamp:
                    return datetime.fromisoformat(timestamp)
            except RedisError as e:
                logger.warning(f"Redis error checking heartbeat: {e}")
        
        return None
    
    async def is_execution_alive(self, execution_id: str) -> bool:
        """Check if an execution is still sending heartbeats"""
        last_heartbeat = await self.check_heartbeat(execution_id)
        if last_heartbeat is None:
            return False
        
        age = (datetime.now() - last_heartbeat).total_seconds()
        return age < settings.HEARTBEAT_TTL
    
    async def cleanup_stale_executions(self) -> List[str]:
        """Find executions that stopped sending heartbeats"""
        stale = []
        running = await self.get_running_executions()
        
        for execution_id in running:
            if not await self.is_execution_alive(execution_id):
                stale.append(execution_id)
        
        return stale
    
    # ==================
    # Caching
    # ==================
    
    async def cache_pipeline(
        self,
        pipeline_id: str,
        data: Dict[str, Any],
        ttl: int = 3600
    ) -> bool:
        """Cache pipeline definition"""
        key = RedisKeys.PIPELINE_CACHE.format(pipeline_id=pipeline_id)
        
        if self._available and self._client:
            try:
                await self._client.set(key, json.dumps(data), ex=ttl)
                return True
            except RedisError as e:
                logger.warning(f"Redis error caching pipeline: {e}")
        
        return False
    
    async def get_cached_pipeline(self, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """Get cached pipeline definition"""
        key = RedisKeys.PIPELINE_CACHE.format(pipeline_id=pipeline_id)
        
        if self._available and self._client:
            try:
                data = await self._client.get(key)
                if data:
                    return json.loads(data)
            except RedisError as e:
                logger.warning(f"Redis error getting cached pipeline: {e}")
        
        return None
    
    async def invalidate_cache(self, pipeline_id: str) -> None:
        """Invalidate pipeline cache"""
        keys = [
            RedisKeys.PIPELINE_CACHE.format(pipeline_id=pipeline_id),
            RedisKeys.STATS_CACHE.format(pipeline_id=pipeline_id)
        ]
        
        if self._available and self._client:
            try:
                await self._client.delete(*keys)
            except RedisError as e:
                logger.warning(f"Redis error invalidating cache: {e}")


# Singleton instance
redis_state_manager = RedisStateManager()
