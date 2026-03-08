import time
from typing import Dict
from app.db.repositories.playback_repo import PlaybackRepository
from fastapi import HTTPException, status


class PlaybackService:

    def __init__(self, playback_repo: PlaybackRepository):
        self.repo = playback_repo


    async def play(self, room_id: str, user_id: str, host_id: str):

        if user_id != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only host can control playback"
            )

        state = await self.repo.get_playback_state(room_id) or {}

        state["is_playing"] = True
        state["start_time"] = time.time()
        state.setdefault("position", 0)

        await self.repo.save_playback_state(room_id, state)

        await self.repo.publish_event(room_id, {
            "type": "play",
            "state": state
        })

        return state


    async def pause(self, room_id: str, user_id: str, host_id: str):

        if user_id != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only host can control playback"
            )

        state = await self.repo.get_state(room_id)

        if not state:
            raise HTTPException(status_code=404, detail="No playback state")

        if state.get("is_playing"):
            elapsed = time.time() - state["start_time"]
            state["position"] += elapsed

        state["is_playing"] = False

        await self.repo.save_state(room_id, state)

        await self.repo.publish_event(room_id, {
            "type": "pause",
            "state": state
        })

        return state

    
    async def seek(self, room_id: str, position: float, user_id: str, host_id: str):

        if user_id != host_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only host can control playback"
            )

        state = await self.repo.get_playback_state(room_id) or {}

        state["position"] = position
        state["start_time"] = time.time()
        state["is_playing"] = True

        await self.repo.save_playback_state(room_id, state)

        await self.repo.publish_event(room_id, {
            "type": "seek",
            "state": state
        })

        return state

    
    async def get_current_position(self, room_id: str):

        state = await self.repo.get_playback_state(room_id)

        if not state:
            return 0

        if state.get("is_playing"):
            elapsed = time.time() - state["start_time"]
            return state["position"] + elapsed

        return state["position"]