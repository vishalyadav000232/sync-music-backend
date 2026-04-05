import json
from typing import Dict, Optional
from redis.asyncio import Redis


class PlaybackRepository:
    
    def __init__(self, redis: Redis):
        self.redis = redis


    def _key(self, room_id: str) -> str:
        return f"room:{room_id}:playback"
    
    

    def _channel(self, room_id: str) -> str:
        return f"room:{room_id}:events"
    
    


    async def save_state(self, room_id: str, state: Dict):
        await self.redis.set(
        self._key(room_id),
        json.dumps(state, default=str)
    )

   
    async def get_state(self, room_id: str) -> Optional[Dict]:
        data = await self.redis.get(self._key(room_id))
        
        if not data:
            return None
        return json.loads(data)
    
    

    async def delete_state(self, room_id: str):
        await self.redis.delete(self._key(room_id))


 
    async def publish_event(self, room_id: str, event: Dict):
        await self.redis.publish(
            self._channel(room_id),
        json.dumps({
            # "room_id": room_id,
            "event": event
        }, default=str)
        )


    
    async def subscribe(self, room_id: str):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self._channel(room_id))
        return pubsub