import asyncio
import logging
from typing import Dict

from app.services.sync_service import get_sync_service, SyncService

logger = logging.getLogger(__name__)

HEARTBEAT_INTERVAL = 1   # seconds
SYNC_TIMEOUT       = 2   # seconds


class HeartbeatScheduler:

    def __init__(self, sync_service: SyncService):
        self.sync_service = sync_service
        self.tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    def is_running(self, room_id: str) -> bool:
        task = self.tasks.get(room_id)
       
        return task is not None and not task.done()

    async def start(self, room_id: str) -> None:
        async with self._lock:
            if self.is_running(room_id):
                return

            async def loop():
                logger.info("Heartbeat started for room %s", room_id)
                try:
                    while True:
                        try:
                            await asyncio.wait_for(
                                self.sync_service.check_room_sync(room_id),
                                timeout=SYNC_TIMEOUT,
                            )
                        except asyncio.TimeoutError:
                            logger.warning("Sync timeout in room %s", room_id)
                        except Exception:
                            logger.exception("Sync error in room %s", room_id)

                        await asyncio.sleep(HEARTBEAT_INTERVAL)

                except asyncio.CancelledError:
                    logger.info("Heartbeat cancelled for room %s", room_id)
                    raise
                finally:
                    async with self._lock:
                        self.tasks.pop(room_id, None)
                    logger.info("Heartbeat task cleaned up for room %s", room_id)

            self.tasks[room_id] = asyncio.create_task(loop())

    async def stop(self, room_id: str) -> None:
        async with self._lock:
            task = self.tasks.get(room_id)
            if not task:
                return
            task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        logger.info("Heartbeat stopped for room %s", room_id)

    async def stop_all(self) -> None:
        async with self._lock:
            room_ids = list(self.tasks.keys())
        for room_id in room_ids:
            await self.stop(room_id)


# ─── Singleton ───────────────────────────────────────────────────────────────

_heartbeat_instance: HeartbeatScheduler | None = None


def get_heartbeat() -> HeartbeatScheduler:
    global _heartbeat_instance
    if _heartbeat_instance is None:
        _heartbeat_instance = HeartbeatScheduler(get_sync_service())
    return _heartbeat_instance