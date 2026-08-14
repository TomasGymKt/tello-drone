import cv2

from UI.elements.Element import Element
from utils.models import Color, AlphaColor, MouseData

class Line(Element):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: Color | AlphaColor, thickness: int = -1):
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        self._color = color
        self._thickness = thickness
        
        self._show_debug_render = False
    
    def handle_mouse(self, mouse: MouseData):
        pass
    
    def render(self, frame):
        opacity = 1.0
        if isinstance(self._color, AlphaColor):
            opacity = self._color.alpha
        
        if opacity == 1.0:
            cv2.line(frame, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
        else:
            overlay = frame.copy()
            cv2.line(overlay, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

        if self._show_debug_render:
            self._debug_render(frame)
    
    def set_debug_render(self, enabled):
        self._show_debug_render = enabled
    
    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
    


class Rectangle(Element):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: Color | AlphaColor, thickness: int = -1):
        self._x1 = x1
        self._x2 = x2
        self._y1 = y1
        self._y2 = y2
        self._color = color
        self._thickness = thickness
        
        self._show_debug_render = False
    
    def handle_mouse(self, mouse: MouseData):
        pass
    
    def render(self, frame):
        opacity = 1.0
        if isinstance(self._color, AlphaColor):
            opacity = self._color.alpha
        
        if opacity == 1.0:
            cv2.rectangle(frame, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
        else:
            overlay = frame.copy()
            cv2.rectangle(overlay, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

        if self._show_debug_render:
            self._debug_render(frame)
    
    def set_debug_render(self, enabled):
        self._show_debug_render = enabled
    
    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
    
