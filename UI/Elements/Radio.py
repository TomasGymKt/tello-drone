from dataclasses import dataclass
from typing import Callable

import cv2

from UI.elements.Element import Element
from UI.elements.Shapes import Rectangle
from utils.common import get_elements_bounding_box, is_mouse_in_bounding_box
from utils.models import AlphaColor, Color, Padding, MouseData


@dataclass(slots=True)
class RadioStyle:
    color: Color = Color(239, 239, 239)
    selected_color: Color = Color(255, 117, 0)
    background_color: AlphaColor = AlphaColor(0, 0, 0, 0.5)
    padding: Padding = Padding(5)
    radius: int = 8
    circle_thickness: int = 2
    circle_text_gap: int = 5
    fontSize: float = 0.6
    fontThickness: int = 1


class Radio:
    def __init__(self, x: int, y: int, text: str, value, style: RadioStyle = RadioStyle()):
        self._original_x = x
        self._original_y = y

        self._x1 = -1
        self._y1 = -1
        self._x2 = -1
        self._y2 = -1

        self._circle_x = -1
        self._circle_y = -1

        self._set_frame_size_on_render = True
        self._show_debug_render = False

        self._text = text
        self._value = value
        self._group: RadioGroup | None = None
        self._style = style

        self.is_hovered = False
        self.is_pressed = False

        self._calculate_text_size()

    @property
    def selected(self) -> bool:
        return self._group.selected is self

    def _calculate_text_size(self):
        (self._text_width, self._text_height), _ = cv2.getTextSize(
            self._text,
            cv2.FONT_HERSHEY_SIMPLEX,
            self._style.fontSize,
            self._style.fontThickness,
        )

    def set_text(self, text: str, style: RadioStyle | None = None):
        if style is None:
            style = self._style

        self._text = text
        self._style = style

        self._calculate_text_size()
        self._set_frame_size_on_render = True

    def set_style(self, style: RadioStyle):
        self._style = style

        self._calculate_text_size()
        self._set_frame_size_on_render = True

    def set_new_frame_size(self, frame):
        frame_height, frame_width = frame.shape[:2]

        content_height = max(self._style.radius * 2, self._text_height)

        width = (self._text_width + self._style.radius * 2 + self._style.circle_text_gap + self._style.padding.horizontal)

        height = content_height + self._style.padding.vertical

        self._x1 = self._original_x
        self._y1 = self._original_y

        if self._original_x < 0:
            self._x1 = frame_width + self._original_x - width

        if self._original_y < 0:
            self._y1 = frame_height + self._original_y - height

        self._x2 = self._x1 + width
        self._y2 = self._y1 + height

        self._circle_x = self._x1 + self._style.padding.left + self._style.radius
        self._circle_y = self._y1 + self._style.padding.top + content_height // 2

    def handle_mouse(self, mouse: MouseData):
        self.is_hovered = is_mouse_in_bounding_box(
            mouse,
            self._x1,
            self._y1,
            self._x2,
            self._y2,
        )

        if mouse.event == cv2.EVENT_LBUTTONDOWN or mouse.event == cv2.EVENT_LBUTTONDBLCLK:
            if self.is_hovered:
                self.is_pressed = True

        elif mouse.event == cv2.EVENT_LBUTTONUP:
            if self.is_pressed and self.is_hovered:
                self._group.select(self)

            self.is_pressed = False

    def render(self, frame):
        if self._set_frame_size_on_render:
            self._set_frame_size_on_render = False
            self.set_new_frame_size(frame)

        opacity = self._style.background_color.alpha

        if self.is_hovered:
            opacity *= 0.9

        if self.is_pressed:
            opacity *= 0.6
        
        Rectangle(
            self._x1, self._y1, self._x2, self._y2,
            AlphaColor(self._style.background_color, opacity)
        ).render(frame)

        color = self._style.selected_color if self.selected else self._style.color

        cv2.circle(frame, (self._circle_x, self._circle_y), self._style.radius, color, self._style.circle_thickness)

        if self.selected:
            cv2.circle(frame, (self._circle_x, self._circle_y), max(1, self._style.radius - self._style.circle_thickness - 1), self._style.selected_color, -1)

        text_x = (self._circle_x + self._style.radius + self._style.circle_text_gap)
        content_height = max(self._style.radius * 2, self._text_height)
        text_y = (self._y1 + self._style.padding.top + (content_height + self._text_height) // 2)

        cv2.putText(frame, self._text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, self._style.fontSize, color, self._style.fontThickness)

        if self._show_debug_render:
            self._debug_render(frame)
    
    def set_debug_render(self, enabled: bool):
        self._show_debug_render = enabled

    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))

        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))

        cv2.line(frame, (self._circle_x - 25, self._circle_y), (self._circle_x + 25, self._circle_y), (0, 255, 0), 1)
        cv2.line(frame, (self._circle_x, self._circle_y - 25), (self._circle_x, self._circle_y + 25), (0, 255, 0), 1)
    

class RadioGroup(Element):
    def __init__(self, callback: Callable[[object], None] | None = None):
        self._radios: list[Radio] = []
        self._selected: Radio | None = None
        self._callback = callback
        
        self._show_debug_render = False

    @property
    def selected(self) -> Radio | None:
        return self._selected

    @property
    def value(self):
        return None if self._selected is None else self._selected._value
    
    @property
    def radios(self) -> list[Radio]:
        return self._radios

    def add(self, radio: Radio):
        if radio._group is not None:
            raise ValueError("Radio already belongs to a RadioGroup")
        
        radio._group = self
        radio.set_debug_render(self._show_debug_render)
        self._radios.append(radio)

    def select(self, radio: Radio):
        self._selected = radio

        if self._callback is not None:
            self._callback(radio._value)

    def handle_mouse(self, mouse: MouseData):
        for radio in self._radios:
            radio.handle_mouse(mouse)

    def set_new_frame_size(self, frame):
        for radio in self._radios:
            radio.set_new_frame_size(frame)

    def render(self, frame):
        for radio in self._radios:
            radio.render(frame)
        
        if self._show_debug_render:
            self._debug_render(frame)

    def set_debug_render(self, enabled: bool):
        self._show_debug_render = enabled
        for radio in self._radios:
            radio.set_debug_render(enabled)
    
    def _debug_render(self, frame):
        box = get_elements_bounding_box(self._radios, include_nested=False)
        if box is None:
            return
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)