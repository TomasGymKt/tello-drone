from __future__ import annotations

import threading


class DebugFrames:
    """Thread-safe frame registry for debug windows rendered on the main thread."""
    
    def __init__(self):
        """Create an empty synchronized debug-frame registry."""
        self._lock = threading.Lock()
        self._frames: dict[str, object] = {}

    def set(self, name: str, frame) -> None:
        """Store a copy of a debug frame under a window name.

        Args:
            name: OpenCV debug-window title.
            frame: Image to copy and expose to the main thread.
        """
        with self._lock:
            self._frames[name] = frame.copy()

    def get_all(self) -> dict[str, object]:
        """Return a snapshot of all registered debug frames.

        Returns:
            Copy of the name-to-frame mapping.
        """
        with self._lock:
            return dict(self._frames)


debug_frames = DebugFrames()
