import cv2

from UI.elements.Element import Element
from utils.common import get_elements_bounding_box
from utils.models import MouseData


class Container(Element):
    """Element that renders and routes input to a collection of child elements."""

    def __init__(self):
        """Create an enabled container with no child elements."""
        super().__init__()
        self._elements: list[Element] = []
        self.enabled = True
        self.opacity = 1.0

    @property
    def elements(self) -> list[Element]:
        """Return the container's child elements.

        Returns:
            The mutable list of child elements in render order.
        """
        return self._elements

    def add(self, element: Element) -> Element:
        """Add an element and synchronize inherited render state.

        Args:
            element: Child element to render and receive mouse events.

        Returns:
            The added element.
        """
        element.set_debug_render(self._show_debug_render)
        if self._frame_width > 0 and self._frame_height > 0:
            element._frame_width = self._frame_width
            element._frame_height = self._frame_height
            element._request_layout()
        self._elements.append(element)
        return element

    def remove(self, element: Element):
        """Remove a child element.

        Args:
            element: Existing child element to remove.
        """
        self._elements.remove(element)

    def clear(self):
        """Remove every child element from the container."""
        self._elements.clear()

    def _handle_mouse(self, mouse: MouseData):
        """Forward a mouse event to children while input is enabled.

        Args:
            mouse: Event type and pointer coordinates to forward.
        """
        if not self.enabled:
            return

        for element in self._elements:
            element.handle_mouse(mouse)

    def _render(self, frame):
        """Render child elements, optionally through an opacity overlay.

        Args:
            frame: OpenCV image that receives child drawings.
        """
        if self.opacity == 1.0:
            for element in self._elements:
                element.render(frame)
        else:
            overlay = frame.copy()
            for element in self._elements:
                element.render(overlay)
            cv2.addWeighted(overlay, self.opacity, frame, 1 - self.opacity, 0, frame)
        
    def set_debug_render(self, enabled: bool):
        """Set debug rendering for this container and its children.

        Args:
            enabled: Whether debug geometry should be visible.
        """
        super().set_debug_render(enabled)
        for element in self._elements:
            element.set_debug_render(enabled)

    def set_style(self, *args, **kwargs):
        """Reject style updates because containers have no local style.

        Raises:
            NotImplementedError: Always, because a container has no local style.
        """
        raise NotImplementedError("Container does not have a local style")

    def set_position(self, *args, **kwargs):
        """Reject position updates because containers have no local geometry.

        Raises:
            NotImplementedError: Always, because a container has no local position.
        """
        raise NotImplementedError("Container does not have a local position")

    def set_new_frame_size(self, frame):
        """Update frame bounds for this container and all children.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        for element in self._elements:
            element.set_new_frame_size(frame)

    def _debug_render(self, frame):
        """Draw a bounding-box overlay around descendant elements.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        box = get_elements_bounding_box(self._elements, include_nested=True)
        if box is None:
            return
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.line(frame, (x2, y1), (x1, y2), (0, 0, 255), 1)
