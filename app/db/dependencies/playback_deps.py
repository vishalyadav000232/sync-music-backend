from app.db.repositories.playback_repo import PlaybackRepository
from app.core.redis import redis_client
from fastapi import Depends
from redis import Redis

def get_playback_repo(redis: Redis = Depends(redis_client)):
    return PlaybackRepository(redis)  