import uuid
import asyncio
from redis.asyncio import Redis
'''
Redis lock is used to prevent the race condition during the user action on the state
'''

class RedisLock:
    def __init__(self, redis: Redis, timeout: int = 5):
        self.redis = redis
        self.timeout = timeout  
        self.lock_value = None

    async def acquire(self, key: str) -> bool:
        self.lock_value = str(uuid.uuid4()) 
        result = await self.redis.set(
            key, self.lock_value, nx=True, ex=self.timeout
        )
        return result is True

    async def release(self, key: str):
        lua = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        await self.redis.eval(lua, 1, key, self.lock_value)