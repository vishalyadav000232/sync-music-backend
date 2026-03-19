import time


class TimeCalculater:
    
    @staticmethod
    async def current_position(state):
        if not state :
            return 0
        if state.get("is_playing"):
            elaps_time = time.monotonic() - state.get("last_update")
            return state["position"] + elaps_time

        return state["position"]
    