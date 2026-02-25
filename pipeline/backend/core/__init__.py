"""Core module initialization."""

from core.distributed_execution import execution_dispatcher

try:  # pragma: no cover - optional redis dependency in minimal test environments
    from core.redis_state import ExecutionState, RedisStateManager, redis_state_manager
except Exception:  # noqa: BLE001
    ExecutionState = None
    RedisStateManager = None
    redis_state_manager = None

__all__ = ["RedisStateManager", "redis_state_manager", "ExecutionState", "execution_dispatcher"]
