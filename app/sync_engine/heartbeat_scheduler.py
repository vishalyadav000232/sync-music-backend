import asyncio
import logging
from fastapi import Depends

from app.services.sync_service import get_sync_service, SyncService

logger = logging.getLogger(__name__)


class HeartbeatScheduler:
    def __init__(self, sync_service: SyncService):
        self.sync_service = sync_service
        self.tasks: dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def start(self, room_id: str):

        async with self._lock:
            if room_id in self.tasks:
                return

            async def loop():
                logger.info(f"Heartbeat started for room {room_id}")

                try:
                    while True:
                        await self.sync_service.check_room_sync(room_id)
                        await asyncio.sleep(3)

                except asyncio.CancelledError:
                    logger.info(f"Heartbeat stopped for room {room_id}")
                    raise

                except Exception as e:
                    logger.exception(f"Heartbeat crashed for room {room_id}: {e}")

            task = asyncio.create_task(loop())
            self.tasks[room_id] = task

    async def stop(self, room_id: str):
        task = self.tasks.get(room_id)

        if not task:
            return

        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        self.tasks.pop(room_id, None)

    async def stop_all(self):
        for room_id in list(self.tasks.keys()):
            await self.stop(room_id)


def get_heartbeat(sync_service: SyncService = Depends(get_sync_service)):
    return HeartbeatScheduler(sync_service)