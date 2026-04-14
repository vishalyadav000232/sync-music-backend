import json
import logging
from redis.asyncio import Redis  

logger = logging.getLogger(__name__)


class PubSub:
    def __init__(self, redis: Redis):
        self.redis = redis

    def channel(self, room_id: str) -> str:
        return f"room:{room_id}:events"

    async def publish(self, room_id: str, event: dict) -> None:
        try:
            await self.redis.publish(self.channel(room_id), json.dumps(event))
        except Exception:
            logger.exception("Failed to publish event to room %s", room_id)

    async def subscribe(self, room_id: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self.channel(room_id))
        return pubsub