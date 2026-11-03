import time


class WaitUtility:
    """Utility class for synchronization and waits."""

    @staticmethod
    def wait_after_action(seconds: int = 2) -> None:
        """Pause after an action when a positive delay is requested."""
        WaitUtility.wait(seconds)

    @staticmethod
    def wait(seconds: int) -> None:
        """Pause for the supplied duration; nonpositive values skip the wait."""
        if seconds > 0:
            time.sleep(seconds)
