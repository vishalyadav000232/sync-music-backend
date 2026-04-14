import uuid
import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisLock:
    def __init__(self, redis: Redis, timeout: int = 5):
        self.redis = redis
        self.timeout = timeout
        self._lock_values: dict[str, str] = {} 

    async def acquire(self, key: str) -> bool:
        value = str(uuid.uuid4())
        result = await self.redis.set(key, value, nx=True, ex=self.timeout)
        if result:
            self._lock_values[key] = value
            logger.debug("Lock acquired: %s", key)
        return bool(result) 

    async def release(self, key: str):
        value = self._lock_values.pop(key, None)
        if not value:
            logger.warning("Tried to release lock not owned: %s", key)
            return

        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        try:
            await self.redis.eval(lua, 1, key, value)
            logger.debug("Lock released: %s", key)
        except Exception:
            logger.exception("Failed to release lock: %s", key)