import cv2

from UI.elements.Element import Element
from utils.common import get_elements_bounding_box
from utils.models import MouseData


class Container(Element):
    def __init__(self):
        super().__init__()
        self._elements: list[Element] = []
        self.enabled = True
        self.opacity = 1.0

    @property
    def elements(self) -> list[Element]:
        return self._elements

    def add(self, element: Element) -> Element:
        element.set_debug_render(self._show_debug_render)
        if self._frame_width > 0 and self._frame_height > 0:
            element._frame_width = self._frame_width
            element._frame_height = self._frame_height
            element._request_layout()
        self._elements.append(element)
        return element

    def remove(self, element: Element):
        self._elements.remove(element)

    def clear(self):
        self._elements.clear()

    def _handle_mouse(self, mouse: MouseData):
        if not self.enabled:
            return

        for element in self._elements:
            element.handle_mouse(mouse)

    def _render(self, frame):
        if self.opacity == 1.0:
            for element in self._elements:
                element.render(frame)
        else:
            overlay = frame.copy()
            for element in self._elements:
                element.render(overlay)
            cv2.addWeighted(overlay, self.opacity, frame, 1 - self.opacity, 0, frame)
        
    def set_debug_render(self, enabled: bool):
        super().set_debug_render(enabled)
        for element in self._elements:
            element.set_debug_render(enabled)

    def set_style(self, *args, **kwargs):
        raise NotImplementedError("Container does not have a local style")

    def set_position(self, *args, **kwargs):
        raise NotImplementedError("Container does not have a local position")

    def set_new_frame_size(self, frame):
        super().set_new_frame_size(frame)
        for element in self._elements:
            element.set_new_frame_size(frame)

    def _debug_render(self, frame):
        box = get_elements_bounding_box(self._elements, include_nested=True)
        if box is None:
            return
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.line(frame, (x2, y1), (x1, y2), (0, 0, 255), 1)
