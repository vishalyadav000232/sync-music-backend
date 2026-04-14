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
      

    async def ensure_listener(self, room_id: str, pub_sub: PubSub, manager) -> None:

       
        async with self._lock:
            if room_id in self._rooms:
                self._rooms[room_id].ref_count += 1
                logger.debug("Room %s ref_count → %d", room_id, self._rooms[room_id].ref_count)
                return
            
            self._rooms[room_id] = None  

       
        try:
            pubsub = await pub_sub.subscribe(room_id)
        except Exception:
            logger.exception("Failed to subscribe to Redis for room %s", room_id)
            async with self._lock:
                self._rooms.pop(room_id, None)
            raise

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

                        asyncio.create_task(manager.broadcast(room_id, event))

                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(
                            "Malformed Redis message in room %s: %s", room_id, e
                        )

            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Redis listener crashed for room %s", room_id)

        state.task = asyncio.create_task(redis_listener())

        async with self._lock:
            self._rooms[room_id] = state

        logger.info("Started Redis listener for room %s", room_id)

    async def release(self, room_id: str) -> None:

        async with self._lock:
            state = self._rooms.get(room_id)

            if state is None:
                return

            state.ref_count -= 1
            logger.info("Room %s ref_count → %d", room_id, state.ref_count)

            if state.ref_count > 0:
                return

            # Ref 0 ho gaya — cleanup karo
            state.task.cancel()

        # Lock ke bahar wait karo
        try:
            await asyncio.wait_for(state.task, timeout=3)
        except asyncio.TimeoutError:
            logger.warning("Force-stopped listener for room %s", room_id)
        except asyncio.CancelledError:
            pass

        try:
            await state.pubsub.unsubscribe()
            await state.pubsub.aclose()
        except Exception:
            logger.exception("Error closing pubsub for room %s", room_id)

        async with self._lock:
            self._rooms.pop(room_id, None)

        logger.info("Shut down listener for room %s", room_id)


registry = RoomListenerRegistry()