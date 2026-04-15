import time
import logging

from app.redis.distributed_lock import RedisLock
from app.redis.pubsub import PubSub
from app.redis.playback_state import PlaybackState
from app.sync_engine.time_calculator import TimeCalculator
from app.utils.song import playlist

logger = logging.getLogger(__name__)


class PlaybackService:
    def __init__(self, state_repo: PlaybackState, pub_sub: PubSub, lock: RedisLock):
        self.state_repo = state_repo
        self.pub_sub = pub_sub
        self.lock = lock
        self._last_seek_time: dict[str, float] = {} 

    # ▶️ PLAY
    async def play(self, room_id: str, user_id: str, host_id: str, song: str, index: int):
        if str(user_id) != str(host_id):
            return

        lock_key = f"lock:play:{room_id}"
        if not await self.lock.acquire(lock_key):
            logger.warning("Could not acquire play lock for room %s", room_id)
            return

        try:
            now = time.time()
            existing = await self.state_repo.get(room_id)

            
            is_same_song = (
                existing is not None
                and existing.get("index") == index
                and existing.get("song") == song
            )

            if is_same_song:
               
                position = float(existing.get("position", 0))
            else:
                
                position = 0.0

            state = {
                "is_playing": True,
                "song": song,
                "index": index,
                "position": position,
                "last_updated": now,
            }

            await self.state_repo.set(room_id, state)

            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "PLAY",
                    "state": state,
                    "server_time": now,
                    "source": user_id,
                }
            })

        except Exception:
            logger.exception("Error during play for room %s", room_id)
        finally:
            await self.lock.release(lock_key)

    # ⏸️ PAUSE
    async def pause(self, room_id: str, user_id: str, host_id: str):
        if str(user_id) != str(host_id):
            return

        lock_key = f"lock:pause:{room_id}"
        if not await self.lock.acquire(lock_key):
            logger.warning("Could not acquire pause lock for room %s", room_id)
            return

        try:
            now = time.time()
            state = await self.state_repo.get(room_id)

            if not state:
                logger.warning("Pause called but no state found for room %s", room_id)
                return

           
            if state.get("is_playing"):
                state["position"] = TimeCalculator.current_position(state)

            state["is_playing"] = False
            state["last_updated"] = now

            await self.state_repo.set(room_id, state)

            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "PAUSE",
                    "state": state,
                    "server_time": now,  
                    "source": user_id,
                }
            })

        except Exception:
            logger.exception("Error during pause for room %s", room_id)
        finally:
            await self.lock.release(lock_key)

    # ⏩ SEEK
    async def seek(self, room_id: str, position: float, user_id: str, host_id: str):
        if str(user_id) != str(host_id):
            return

        now = time.time()

        last_time = self._last_seek_time.get(room_id, 0)
        if now - last_time < 0.3:
            return
        self._last_seek_time[room_id] = now

        lock_key = f"lock:seek:{room_id}"
        if not await self.lock.acquire(lock_key):
            logger.warning("Could not acquire seek lock for room %s", room_id)
            return

        try:
            state = await self.state_repo.get(room_id)
            if not state:
                return

            # Threshold 0.1s — 1s bahut coarse tha
            current = TimeCalculator.current_position(state)
            if abs(current - position) < 0.1:
                return

            state["position"] = position
            state["last_updated"] = now

            await self.state_repo.set(room_id, state)

            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "SEEK",
                    "state": state,
                    "server_time": now,  # Fix #12
                    "source": user_id,
                }
            })

        except Exception:
            logger.exception("Error during seek for room %s", room_id)
        finally:
            await self.lock.release(lock_key)

    async def next(self, room_id: str, user_id: str, host_id: str):
        if str(user_id) != str(host_id):
            return

        lock_key = f"lock:next:{room_id}"
        if not await self.lock.acquire(lock_key):
            logger.warning("Could not acquire next lock for room %s", room_id)
            return

        try:
            now = time.time()
            state = await self.state_repo.get(room_id) or {}
            current_index = int(state.get("index", -1))
            next_index = (current_index + 1) % len(playlist)

            state = {
                "is_playing": True,
                "song": playlist[next_index],
                "index": next_index,
                "position": 0.0,
                "last_updated": now,
            }

            await self.state_repo.set(room_id, state)
            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "NEXT",
                    "state": state,
                    "server_time": now,
                    "source": user_id,
                }
            })
        except Exception:
            logger.exception("Error during next for room %s", room_id)
        finally:
            await self.lock.release(lock_key)

    async def prev(self, room_id: str, user_id: str, host_id: str):
        if str(user_id) != str(host_id):
            return

        lock_key = f"lock:prev:{room_id}"
        if not await self.lock.acquire(lock_key):
            logger.warning("Could not acquire prev lock for room %s", room_id)
            return

        try:
            now = time.time()
            state = await self.state_repo.get(room_id) or {}
            current_index = int(state.get("index", 0))
            prev_index = (current_index - 1) % len(playlist)

            state = {
                "is_playing": True,
                "song": playlist[prev_index],
                "index": prev_index,
                "position": 0.0,
                "last_updated": now,
            }

            await self.state_repo.set(room_id, state)
            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "PREV",
                    "state": state,
                    "server_time": now,
                    "source": user_id,
                }
            })
        except Exception:
            logger.exception("Error during prev for room %s", room_id)
        finally:
            await self.lock.release(lock_key)

    async def get_current_position(self, room_id: str) -> float:
        state = await self.state_repo.get(room_id)
        if not state:
            return 0.0
        return TimeCalculator.current_position(state)  # sync call — no await needed