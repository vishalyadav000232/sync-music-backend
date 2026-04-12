import time
from app.websocket.manager import ConnectionManager

class SyncBroadcaster:

    def __init__(self, manager : ConnectionManager):
        self.manager = manager

    async def broadcast_sync(self, room_id, position):

        now = time.time()

        await self.manager.broadcast(room_id, {
            "event": {
                "type": "SYNC",
                "position": position,
                "server_time": now
            }
        })