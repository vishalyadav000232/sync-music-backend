class SyncBroadcaster:

    def __init__(self, manager):
        self.manager = manager

    async def broadcast_sync(self, room_id, position):

        await self.manager.broadcast(room_id, {
            "type": "sync",
            "position": position
        })