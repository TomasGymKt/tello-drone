from dataclasses import dataclass
from typing import Callable

import cv2

from UI.elements.Element import Element
from UI.elements.Shapes import Rectangle
from utils.common import is_mouse_in_bounding_box
from utils.models import AlphaColor, Color, Padding, MouseData


@dataclass(slots=True)
class ButtonStyle:
    color: Color = Color(220, 220, 220)
    background_color: AlphaColor = AlphaColor(0, 0, 0, 1.0)
    hoverd_color: Color | None = None
    hoverd_background_color: AlphaColor | None = None
    pressed_color: Color | None = None
    pressed_background_color: AlphaColor | None = None
    padding: Padding = Padding(5)
    fontSize: float = 0.6
    fontThickness: int = 1

class Button(Element):
    def __init__(self, x: int, y: int, text: str, callback: Callable[[], None], style: ButtonStyle = ButtonStyle()):
        super().__init__()
        self._original_x = 0
        self._original_y = 0
        self._x1 = -1
        self._y1 = -1
        self._x2 = -1
        self._y2 = -1
        self._callback = callback
        
        self._text = text
        self._style = style
        
        self.is_hovered = False
        self.is_pressed = False
        
        self._calculate_text_size()
        self.set_position(x, y)
        
    def _calculate_text_size(self):
        (self._text_width, self._text_height), _ = cv2.getTextSize(
            self._text,
            cv2.FONT_HERSHEY_SIMPLEX,
            self._style.fontSize,
            self._style.fontThickness,
        )

    def set_text(self, text: str, style: ButtonStyle | None = None):
        if style is None:
            style = self._style

        self._text = text
        self._style = style

        self._calculate_text_size()
        self.set_position()

    def set_position(self, x: int | None = None, y: int | None = None):
        if x is not None:
            self._original_x = x
        if y is not None:
            self._original_y = y

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()

    def set_style(self, style: ButtonStyle):
        self._style = style

        self._calculate_text_size()
        self.set_position()
    
    def set_new_frame_size(self, frame):
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        self._x1 = self._original_x
        self._y1 = self._original_y
        
        if self._original_x < 0:
            self._x1 = self._frame_width + self._original_x - self._text_width - self._style.padding.horizontal
    
        if self._original_y < 0:
            self._y1 = self._frame_height + self._original_y - self._text_height - self._style.padding.vertical
        
        self._x2 = self._x1 + self._text_width + self._style.padding.horizontal
        self._y2 = self._y1 + self._text_height + self._style.padding.vertical
    
    def _handle_mouse(self, mouse: MouseData):
        self.is_hovered = is_mouse_in_bounding_box(mouse, self._x1, self._y1, self._x2, self._y2)

        if mouse.event == cv2.EVENT_LBUTTONDOWN or mouse.event == cv2.EVENT_LBUTTONDBLCLK:
            if self.is_hovered:
                self.is_pressed = True

        elif mouse.event == cv2.EVENT_LBUTTONUP:
            if self.is_pressed and self.is_hovered:
                self._callback()

            self.is_pressed = False
    
    def _render(self, frame):
        color = self._style.color
        background_color = self._style.background_color

        if self.is_hovered:
            color = self._style.hoverd_color or self._style.color
            background_color = self._style.hoverd_background_color or AlphaColor(self._style.background_color, self._style.background_color.alpha*0.8)
        
        if self.is_pressed:
            color = self._style.pressed_color or self._style.color
            background_color = self._style.pressed_background_color or AlphaColor(self._style.background_color, self._style.background_color.alpha*0.6)
            
        
        Rectangle(
            self._x1, self._y1, self._x2, self._y2,
            AlphaColor(background_color, background_color.alpha)
        ).render(frame)
        cv2.putText(frame, self._text, (self._x1 + self._style.padding.left, self._y1 + self._text_height + self._style.padding.top), cv2.FONT_HERSHEY_SIMPLEX, self._style.fontSize, color, self._style.fontThickness)
    
    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
