import cv2
from dataclasses import dataclass

from UI.elements.Element import Element
from UI.elements.Shapes import Rectangle
from utils.models import Color, AlphaColor, MouseData, Padding

@dataclass(slots=True)
class TextStyle:
    color: Color = Color(255, 255, 255)
    background_color: AlphaColor = AlphaColor(0, 0, 0, 0.5)
    
    padding: Padding = Padding(5)
    fontSize: float = 0.6
    fontThickness: int = 1


class Text(Element):
    def __init__(self, x: int, y: int, text: str, style: TextStyle = TextStyle()):
        self._original_x = x
        self._original_y = y
        self._x1 = -1
        self._y1 = -1
        self._x2 = -1
        self._y2 = -1
        
        self._text = text
        self._style = style
        
        self._set_frame_size_on_render = True
        self._show_debug_render = False
        
        self._calculate_text_size()
        
    def _calculate_text_size(self):
        (self._text_width, self._text_height), _ = cv2.getTextSize(
            self._text,
            cv2.FONT_HERSHEY_SIMPLEX,
            self._style.fontSize,
            self._style.fontThickness,
        )

    def set_text(self, text: str, style: TextStyle | None = None):
        if style is None:
            style = self._style

        self._text = text
        self._style = style

        self._calculate_text_size()
        self._set_frame_size_on_render = True
    
    def set_position(self, x: int | None = None, y: int | None = None):
        if x is not None:
            self._original_x = x
        if y is not None:
            self._original_y = y
        
        self._set_frame_size_on_render = True


    def set_style(self, style: TextStyle):
        self._style = style

        self._calculate_text_size()
        self._set_frame_size_on_render = True
    
    def set_new_frame_size(self, frame):
        frame_height, frame_width = frame.shape[:2]
        
        self._x1 = self._original_x
        self._y1 = self._original_y
        
        if self._original_x < 0:
            self._x1 = frame_width + self._original_x - self._text_width - self._style.padding.horizontal
    
        if self._original_y < 0:
            self._y1 = frame_height + self._original_y - self._text_height - self._style.padding.vertical
        
        self._x2 = self._x1 + self._text_width + self._style.padding.horizontal
        self._y2 = self._y1 + self._text_height + self._style.padding.vertical
    
    def handle_mouse(self, mouse: MouseData):
        pass
    
    def render(self, frame):
        if self._set_frame_size_on_render:
            self._set_frame_size_on_render = False
            self.set_new_frame_size(frame)
        
        Rectangle(
            self._x1, self._y1, self._x2, self._y2,
            self._style.background_color
        ).render(frame)
        cv2.putText(frame, self._text, (self._x1 + self._style.padding.left, self._y1 + self._text_height + self._style.padding.top), cv2.FONT_HERSHEY_SIMPLEX, self._style.fontSize, self._style.color, self._style.fontThickness)
        
        if self._show_debug_render:
            self._debug_render(frame)
    
    def set_debug_render(self, enabled: bool):
        self._show_debug_render = enabled
    
    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))