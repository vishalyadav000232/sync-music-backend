import time
import logging

logger = logging.getLogger(__name__)

DRIFT_THRESHOLD = 0.2
from app.sync_engine.time_calculator import TimeCalculator
from app.redis.client import get_redis
from app.redis.playback_state import PlaybackState
from app.redis.pubsub import PubSub

class SyncService:

    def __init__(self, playback_repo, pub_sub):
        self.state_repo = playback_repo
        self.pub_sub = pub_sub
        self.last_positions = {}

    async def check_room_sync(self, room_id: str):
        try:
            state = await self.state_repo.get(room_id)
        except Exception as e:
            logger.exception(f"❌ Redis error in room {room_id}: {e}")
            return

        if not state:
            return

        is_playing = state.get("is_playing", False)

        position = TimeCalculator.current_position(state)
        now = time.monotonic()

        last_pos = self.last_positions.get(room_id)

        # ✅ Drift detection
        if last_pos is not None and abs(position - last_pos) < DRIFT_THRESHOLD:
            return

        self.last_positions[room_id] = position

        await self.pub_sub.publish(room_id, {
            "event": {
                "type": "SYNC",
                "state": {**state, "position": position},
                "server_time": now,
                "source": "server",
            }
        })

def get_sync_service():
    redis = get_redis()
    playback_repo = PlaybackState(redis)
    pub_sub = PubSub(redis)

    return SyncService(playback_repo, pub_sub)