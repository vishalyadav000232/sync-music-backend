import asyncio

class HeartbeatScheduler:

    def __init__(self, sync_service):
        self.sync_service = sync_service

    async def start(self, room_id):

        while True:

            await self.sync_service.check_room_sync(room_id)

            await asyncio.sleep(3)