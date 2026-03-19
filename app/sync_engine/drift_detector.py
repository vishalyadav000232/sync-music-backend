class DriftDetector:

    DRIFT_THRESHOLD = 0.5

    @staticmethod
    def detect(server_position, client_position):

        drift = abs(server_position - client_position)

        if drift > DriftDetector.DRIFT_THRESHOLD:
            return True, drift

        return False, drift