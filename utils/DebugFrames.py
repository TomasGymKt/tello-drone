from __future__ import annotations

import threading


class DebugFrames:
    """
    a class to make frames available across threads
    useful for showing windows from non-main threads
    should be used only for debuging, since permanent windows should be done with the WindowsController
    """
    
    def __init__(self):
        self._lock = threading.Lock()
        self._frames: dict[str, object] = {}

    def set(self, name: str, frame) -> None:
        with self._lock:
            self._frames[name] = frame.copy()

    def get_all(self) -> dict[str, object]:
        with self._lock:
            return dict(self._frames)


debug_frames = DebugFrames()

