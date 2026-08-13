import cv2

from UI.Elements.Element import Element
from utils.common import get_elements_bounding_box
from utils.models import MouseData


class Container(Element):
    def __init__(self):
        self._elements: list[Element] = []
        self.visible = True
        self.enabled = True
        
        self._show_debug_render = False

    @property
    def elements(self) -> list[Element]:
        return self._elements

    def add(self, element: Element) -> Element:
        element.set_debug_render(self._show_debug_render)
        self._elements.append(element)
        return element

    def remove(self, element: Element):
        self._elements.remove(element)

    def clear(self):
        self._elements.clear()

    def handle_mouse(self, mouse: MouseData):
        if not self.visible or not self.enabled:
            return

        for element in self._elements:
            element.handle_mouse(mouse)

    def render(self, frame):
        if not self.visible:
            return

        for element in self._elements:
            element.render(frame)
        
        if self._show_debug_render:
            self._debug_render(frame)
    
    def set_debug_render(self, enabled: bool):
        self._show_debug_render = enabled
        for element in self._elements:
            element.set_debug_render(enabled)
    
    def _debug_render(self, frame):
        x1, y1, x2, y2 = get_elements_bounding_box(self._elements, include_nested=True)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.line(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.line(frame, (x2, y1), (x1, y2), (0, 0, 255), 1)