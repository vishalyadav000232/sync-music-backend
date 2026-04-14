import json
import logging
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

STATE_TTL = 86400  


class PlaybackState:
    def __init__(self, redis: Redis):
        self.redis = redis

    def key(self, room_id: str) -> str:
        return f"room:{room_id}:state"

    async def get(self, room_id: str) -> dict | None:
        try:
            data = await self.redis.get(self.key(room_id))
            return json.loads(data) if data else None
        except Exception:
            logger.exception("Failed to get state for room %s", room_id)
            return None

    async def set(self, room_id: str, state: dict) -> None:
        try:
            await self.redis.set(
                self.key(room_id),
                json.dumps(state),
                ex=STATE_TTL, 
            )
        except Exception:
            logger.exception("Failed to set state for room %s", room_id)

    async def delete(self, room_id: str) -> None:
        try:
            await self.redis.delete(self.key(room_id))
        except Exception:
            logger.exception("Failed to delete state for room %s", room_id)