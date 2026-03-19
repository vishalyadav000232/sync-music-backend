from app.db.repositories.playback_repo import PlaybackRepository
from app.core.redis import get_redis
from fastapi import Depends
from redis.asyncio import Redis

async def get_playback_repo(redis: Redis = Depends(get_redis)):
    return PlaybackRepository(redis)