from abc import ABC, abstractmethod

from utils.models import MouseData

class Element(ABC):
    """Base contract for a drawable, optionally interactive UI element."""

    def handle_mouse(self, mouse: MouseData):
        """Handle a mouse event when the element is visible.

        Args:
            mouse: Event type and pointer coordinates to process.
        """
        if not self.visible:
            return

        self._handle_mouse(mouse)

    def _handle_mouse(self, mouse: MouseData):
        """Implement element-specific mouse handling.

        Args:
            mouse: Event type and pointer coordinates to process.
        """
        pass

    def render(self, frame):
        """Lay out and draw the element when it is visible.

        Args:
            frame: OpenCV image that receives the element drawing.
        """
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
        """Draw the element without visibility or debug handling.

        Args:
            frame: OpenCV image that receives the element drawing.
        """
        ...

    def set_debug_render(self, enabled: bool):
        """Enable or disable the element's debug overlay.

        Args:
            enabled: Whether to render debug geometry.
        """
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
        """Store dimensions from a new rendering frame.

        Args:
            frame: OpenCV image whose dimensions define the layout bounds.
        """
        self._frame_height, self._frame_width = frame.shape[:2]
        self._set_frame_size_on_render = False

    def _request_layout(self):
        """Resolve geometry on the next render when a frame is available."""
        self._set_frame_size_on_render = True

    def _debug_render(self, frame):
        """Draw optional debug geometry for the element.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        pass

    def __init__(self):
        """Initialize shared visibility, debug, and layout state."""
        self._show_debug_render = False
        self.visible = True
        self._set_frame_size_on_render = False
        self._frame_width = -1
        self._frame_height = -1

