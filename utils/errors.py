class ConnectionError(Exception):
    """Raised when the application cannot connect to the Tello drone."""

    def __init__(self, msg: str):
        """Create a connection error.

        Args:
            msg: Human-readable connection failure description.
        """
        self.msg = msg

class ScanningError(Exception):
    """Raised when a scanner backend encounters a recoverable failure."""

    def __init__(self, scanning_method: str, base_error: Exception, msg: str = ""):
        """Create a scanner failure with the original exception.

        Args:
            scanning_method: Identifier of the failed scanner backend.
            base_error: Original exception raised by the backend.
            msg: Optional additional context.
        """
        self.scanning_method = scanning_method
        self.base_error = base_error
        self.msg = msg
