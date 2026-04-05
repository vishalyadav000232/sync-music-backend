

import json

class PlaybackState:
    def __init__(self, redis):
        self.redis = redis

    def key(self, room_id):
        return f"room:{room_id}:state"

    async def get(self, room_id):
        data = await self.redis.get(self.key(room_id))
        return json.loads(data) if data else None

    async def set(self, room_id, state):
        await self.redis.set(self.key(room_id), json.dumps(state))