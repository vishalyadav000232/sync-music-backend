import time


class TimeCalculator: 
    
    @staticmethod
    def current_position(state):
        if not state:
            return 0

        position = state.get("position", 0)
        last_updated = state.get("last_updated")

        if state.get("is_playing") and last_updated:
            now = time.time()
            elapsed = now - last_updated
            return position + elapsed

        return position