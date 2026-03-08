from redis import Redis
import json
from typing import Dict

class PlaybackRepository:
    
    def __init__(self , redis : Redis):
        self.redis = redis
    def _key(self, room_id: str) -> str:
        return f"room:{room_id}:playback"
        
    async def save_playback_state(self , room_id , state):
        await self.redis.set(
            name= self._key(room_id),
            value=json.dump(state)
        )
        
    
    async def get_playback_state(self , room_id):
        data =  await self.redis.get(
            name=self._key(room_id)
        )
        if not data :
            raise ValueError("redis have no playbck")
        return json.loads(data)
    
    async def delete_playback_state(self , room_id):
        await self.redis.delete(
            self._key(room_id)
        )
        
    async def publish_event(self, room_id: str, event: Dict):
        await self.redis.publish(
            "room_events",
            json.dumps({
                "room_id": room_id,
                "event": event
            })
        )
    async def subscribe(self):
        pubsub = self.redis.pubsub()
        await pubsub.subscribe("room_events")
        return pubsub
    
