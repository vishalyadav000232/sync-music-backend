from redis.asyncio import Redis

redis_client = Redis(
    host="redis",
    port=6379,
    decode_responses=True
)

def get_redis():
    return redis_client