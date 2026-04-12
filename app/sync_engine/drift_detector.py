class DriftDetector:

    HARD_THRESHOLD = 0.5   # big jump
    SOFT_THRESHOLD = 0.15  # smooth correction

    @staticmethod
    def detect(server_position, client_position):

        drift = server_position - client_position
        abs_drift = abs(drift)

        if abs_drift > DriftDetector.HARD_THRESHOLD:
            return {
                "action": "HARD_SYNC",  # jump
                "drift": drift
            }

        elif abs_drift > DriftDetector.SOFT_THRESHOLD:
            return {
                "action": "SOFT_SYNC",  # speed adjust
                "drift": drift
            }

        return {
            "action": "NONE",
            "drift": drift
        }