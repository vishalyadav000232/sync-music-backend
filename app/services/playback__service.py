import time
from app.redis.distributed_lock import RedisLock
from app.redis.pubsub import PubSub
from app.redis.playback_state import PlaybackState
class PlaybackService:
    def __init__(self, state_repo :PlaybackState , pub_sub : PubSub, lock : RedisLock):
        self.state_repo = state_repo
        self.pub_sub = pub_sub
        self.lock = lock
        self.last_seek = {}  

  
    async def play(self, room_id, user_id, host_id, song, index):

        if str(user_id) != str(host_id):
            return

        lock_key = f"lock:play:{room_id}"

        if not await self.lock.acquire(lock_key):
            return

        try:
            now = time.time()

            state = {
                "is_playing": True,
                "song": song,
                "index": index,
                "position": 0,
                "last_updated": now
            }

            await self.state_repo.set(room_id, state)

            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "PLAY",
                    "state": state,
                    "source": "server"
                }
            })

        finally:
            await self.lock.release(lock_key)

   
    async def pause(self, room_id, user_id, host_id):

        if str(user_id) != str(host_id):
            return

        lock_key = f"lock:pause:{room_id}"

        if not await self.lock.acquire(lock_key):
            return

        try:
            now = time.time()
            state = await self.state_repo.get(room_id)

            if not state:
                return

            
            if state["is_playing"]:
                state["position"] += (now - state["last_updated"])

            state["is_playing"] = False
            state["last_updated"] = now

            await self.state_repo.set(room_id, state)

            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "PAUSE",
                    "state": state,
                    "source": "server"
                }
            })

        finally:
            await self.lock.release(lock_key)

    async def seek(self, room_id, position, user_id, host_id):

        if str(user_id) != str(host_id):
            return

        now = time.time()

       
        last = self.last_seek.get(room_id, 0)
        if now - last < 0.5:
            return

        self.last_seek[room_id] = now

        lock_key = f"lock:seek:{room_id}"

        if not await self.lock.acquire(lock_key):
            return

        try:
            state = await self.state_repo.get(room_id)

            if not state:
                return

            state["position"] = position
            state["last_updated"] = now

            await self.state_repo.set(room_id, state)

            await self.pub_sub.publish(room_id, {
                "event": {
                    "type": "SEEK",
                    "state": state,
                    "source": "server"
                }
            })

        finally:
            await self.lock.release(lock_key)