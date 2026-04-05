import json
from redis import Redis
class PubSub:
    def __init__(self, redis : Redis):
        self.redis = redis

    def channel(self, room_id):
        return f"room:{room_id}:events"

    async def publish(self, room_id, event):
        await self.redis.publish(self.channel(room_id), json.dumps(event))

    async def subscribe(self, room_id):
        pubsub =  self.redis.pubsub()
        await pubsub.subscribe(self.channel(room_id))
        return pubsub