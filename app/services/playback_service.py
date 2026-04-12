import time
from app.db.repositories.playback_repo import PlaybackRepository
from app.sync_engine.time_calculator import TimeCalculator


class PlaybackService:
    def __init__(self, playback_repo: PlaybackRepository):
        self.repo = playback_repo

    def _now(self):
        return time.time()   

    async def play(self, room_id: str, user_id: str, host_id: str):

        if str(user_id) != str(host_id):
            return {"error": "Only host can control playback"}

        state = await self.repo.get_state(room_id) or {}

        now = self._now()

        if not state.get("is_playing"):
            state["last_updated"] = now

        state["is_playing"] = True
        state.setdefault("position", 0)
        state["server_time"] = now

        await self.repo.save_state(room_id, state)

        event = {
            "event": {
                "type": "PLAY",
                "state": state,
                "server_time": now
            }
        }

        await self.repo.publish_event(room_id, event)
        return event

    async def pause(self, room_id: str, user_id: str, host_id: str):

        if str(user_id) != str(host_id):
            return {"error": "Only host can control playback"}

        state = await self.repo.get_state(room_id)
        if not state:
            return {"error": "No playback state"}

        now = self._now()

        if state.get("is_playing"):
            current_pos = await TimeCalculator.current_position(state)
            state["position"] = current_pos

        state["is_playing"] = False
        state["last_updated"] = now
        state["server_time"] = now

        await self.repo.save_state(room_id, state)

        event = {
            "event": {
                "type": "PAUSE",
                "state": state,
                "server_time": now
            }
        }

        await self.repo.publish_event(room_id, event)
        return event

    async def seek(self, room_id: str, position: float, user_id: str, host_id: str):

        if str(user_id) != str(host_id):
            return {"error": "Only host can control playback"}

        state = await self.repo.get_state(room_id) or {}

        now = self._now()

        state["position"] = position
        state["last_updated"] = now
        state["server_time"] = now
        state["is_playing"] = state.get("is_playing", True)

        await self.repo.save_state(room_id, state)

        event = {
            "event": {
                "type": "SEEK",
                "state": state,
                "server_time": now
            }
        }

        await self.repo.publish_event(room_id, event)
        return event

    async def get_current_position(self, room_id: str):
        state = await self.repo.get_state(room_id)
        if not state:
            return 0

        return await TimeCalculator.current_position(state)