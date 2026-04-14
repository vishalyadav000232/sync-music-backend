import time
import logging

logger = logging.getLogger(__name__)


class TimeCalculator:

    @staticmethod
    def current_position(state: dict) -> float:
        if not state:
            return 0.0

        position = float(state.get("position", 0))
        last_updated = state.get("last_updated")

        if state.get("is_playing") and last_updated:
            elapsed = time.time() - float(last_updated)
            
            if 0 <= elapsed <= 86400:
                return position + elapsed
            else:
                logger.warning(
                    "Suspicious elapsed time: %.2f — returning raw position",
                    elapsed,
                )

        return position