from abc import ABC, abstractmethod

from utils.models import MouseData

class Element(ABC):
    def handle_mouse(self, mouse: MouseData):
        if not self.visible:
            return

        self._handle_mouse(mouse)

    def _handle_mouse(self, mouse: MouseData):
        pass

    def render(self, frame):
        if self._set_frame_size_on_render:
            self._set_frame_size_on_render = False
            self.set_new_frame_size(frame)

        if not self.visible:
            return

        self._render(frame)

        if self._show_debug_render:
            self._debug_render(frame)

    @abstractmethod
    def _render(self, frame):
        ...

    def set_debug_render(self, enabled: bool):
        self._show_debug_render = enabled

    @abstractmethod
    def set_style(self, *args, **kwargs):
        """Update this element's visual style."""
        ...

    @abstractmethod
    def set_position(self, *args, **kwargs):
        """Update source coordinates and resolve them against the current frame."""
        ...

    def set_new_frame_size(self, frame):
        self._frame_height, self._frame_width = frame.shape[:2]
        self._set_frame_size_on_render = False

    def _request_layout(self):
        """Resolve geometry on the next render when a frame is available."""
        self._set_frame_size_on_render = True

    def _debug_render(self, frame):
        pass

    def __init__(self):
        self._show_debug_render = False
        self.visible = True
        self._set_frame_size_on_render = False
        self._frame_width = -1
        self._frame_height = -1

