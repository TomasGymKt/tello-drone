from __future__ import annotations

import threading
import numpy as np


class DebugFrames:
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


def create_blank_frame(width: int, height: int, color: tuple[int, int, int] = (255, 255, 255)):
    frame = np.full((width, height, 3), color, dtype=np.uint8)
    return frame