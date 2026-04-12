import asyncio
import json
import logging

from app.websocket.roomstate import RoomState
from app.redis.pubsub import PubSub
logger = logging.getLogger(__name__)


class RoomListenerRegistry:
    def __init__(self):
        self._rooms: dict[str, RoomState] = {}
        self._lock = asyncio.Lock()
        
        print(self._rooms)

    async def ensure_listener(self, room_id: str, playback_repo :PubSub , manager):

        async with self._lock:
            if room_id in self._rooms:
                self._rooms[room_id].ref_count += 1
                return

            pubsub = await playback_repo.subscribe(room_id)
            state = RoomState(pubsub=pubsub, ref_count=1)

            async def redis_listener():
                try:
                    async for message in pubsub.listen():

                        if message["type"] != "message":
                            continue

                        try:
                            raw = message["data"]

                         
                            if isinstance(raw, bytes):
                                raw = raw.decode("utf-8")

                            data = json.loads(raw)

                           
                            event = data.get("event")
                            if not event:
                                continue

                            asyncio.create_task(
                                manager.broadcast(room_id, event)
                            )

                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(
                                "Malformed Redis message in room %s: %s",
                                room_id,
                                e
                            )

                except asyncio.CancelledError:
                    raise

                except Exception:
                    logger.exception(
                        "Redis listener crashed for room %s",
                        room_id
                    )

            state.task = asyncio.create_task(redis_listener())
            self._rooms[room_id] = state

            logger.info("Started listener for room %s", room_id)

    async def release(self, room_id: str):

        async with self._lock:
            state = self._rooms.get(room_id)

            if state is None:
                return

            state.ref_count -= 1

            logger.info(
                "Room %s now has %d connected user(s)",
                room_id,
                state.ref_count
            )

            if state.ref_count > 0:
                return

           

            state.task.cancel()

            try:
                
                await asyncio.wait_for(state.task, timeout=3)

            except asyncio.TimeoutError:
                logger.warning(
                    "Force stopping listener for room %s",
                    room_id
                )

            except asyncio.CancelledError:
                pass

            try:
                await state.pubsub.unsubscribe()
                await state.pubsub.aclose()

            except Exception:
                logger.exception(
                    "Error closing pubsub for room %s",
                    room_id
                )

            del self._rooms[room_id]

            logger.info("Shut down listener for room %s", room_id)


registry = RoomListenerRegistry()