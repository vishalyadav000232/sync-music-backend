import time
from app.redis.playback_state import PlaybackState
from app.sync_engine.time_calculator import TimeCalculator
from app.redis.pubsub import PubSub
from app.redis.client import get_redis


class SyncService:

    def __init__(self, playback_repo: PlaybackState, pub_sub: PubSub):
        self.state_repo = playback_repo
        self.pub_sub = pub_sub

    async def check_room_sync(self, room_id: str):

        state = await self.state_repo.get(room_id)

        if not state or not state.get("is_playing", False):
            return

        position =  TimeCalculator.current_position(state)
        now = time.time()

        await self.pub_sub.publish(room_id, {
            "event": {
                "type": "SYNC",
                "position": position,
                "server_time": now
            }
        })


def get_sync_service():
    redis = get_redis()
    playback_repo = PlaybackState(redis)
    pub_sub = PubSub(redis)

    return SyncService(playback_repo, pub_sub)