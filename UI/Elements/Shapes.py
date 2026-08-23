import cv2

from UI.elements.Container import Container
from UI.elements.Element import Element
from utils.models import Color, AlphaColor, Int_Vector2, MouseData

class Line(Element):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: Color | AlphaColor, thickness: int = 1):
        super().__init__()
        self._original_x1 = 0
        self._original_x2 = 0
        self._original_y1 = 0
        self._original_y2 = 0
        self._x1 = -1
        self._x2 = -1
        self._y1 = -1
        self._y2 = -1
        self._color = color
        self._thickness = thickness
        self.set_position(x1, y1, x2, y2)
        
    def set_style(self, color: Color | AlphaColor | None = None, thickness: int | None = None):
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
    
    def set_position(self, x1: int | None = None, y1: int | None = None, x2: int | None = None, y2: int | None = None):
        if x1 is not None:
            self._original_x1 = x1
        if y1 is not None:
            self._original_y1 = y1
        if x2 is not None:
            self._original_x2 = x2
        if y2 is not None:
            self._original_y2 = y2

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()

    def set_new_frame_size(self, frame):
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        self._x1 = self._resolve_x(self._original_x1)
        self._y1 = self._resolve_y(self._original_y1)
        self._x2 = self._resolve_x(self._original_x2)
        self._y2 = self._resolve_y(self._original_y2)

    def _resolve_x(self, x: int) -> int:
        return self._frame_width + x if x < 0 else x

    def _resolve_y(self, y: int) -> int:
        return self._frame_height + y if y < 0 else y
    
    def _handle_mouse(self, mouse: MouseData):
        pass

    def _render(self, frame):
        opacity = 1.0
        if isinstance(self._color, AlphaColor):
            opacity = self._color.alpha
        
        if opacity == 1.0:
            cv2.line(frame, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
        else:
            overlay = frame.copy()
            cv2.line(overlay, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
    


class Rectangle(Element):
    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: Color | AlphaColor, thickness: int = -1):
        super().__init__()
        self._original_x1 = 0
        self._original_x2 = 0
        self._original_y1 = 0
        self._original_y2 = 0
        self._x1 = -1
        self._x2 = -1
        self._y1 = -1
        self._y2 = -1
        self._color = color
        self._thickness = thickness
        self.set_position(x1, y1, x2, y2)
        
    def set_style(self, color: Color | AlphaColor | None = None, thickness: int | None = None):
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness

    def set_position(self, x1: int | None = None, y1: int | None = None, x2: int | None = None, y2: int | None = None):
        if x1 is not None:
            self._original_x1 = x1
        if y1 is not None:
            self._original_y1 = y1
        if x2 is not None:
            self._original_x2 = x2
        if y2 is not None:
            self._original_y2 = y2

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()

    def set_new_frame_size(self, frame):
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        self._x1 = self._frame_width + self._original_x1 if self._original_x1 < 0 else self._original_x1
        self._y1 = self._frame_height + self._original_y1 if self._original_y1 < 0 else self._original_y1
        self._x2 = self._frame_width + self._original_x2 if self._original_x2 < 0 else self._original_x2
        self._y2 = self._frame_height + self._original_y2 if self._original_y2 < 0 else self._original_y2
    
    def _handle_mouse(self, mouse: MouseData):
        pass

    def _render(self, frame):
        opacity = 1.0
        if isinstance(self._color, AlphaColor):
            opacity = self._color.alpha
        
        if opacity == 1.0:
            cv2.rectangle(frame, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
        else:
            overlay = frame.copy()
            cv2.rectangle(overlay, (self._x1, self._y1), (self._x2, self._y2), self._color, self._thickness)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

    def _debug_render(self, frame):
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
    

class Circle(Element):
    def __init__(self, x: int, y: int, radius: int, color: Color | AlphaColor, thickness: int = -1):
        super().__init__()
        self._original_x = 0
        self._original_y = 0
        self._x = -1
        self._y = -1
        self._radius = radius
        
        self._color = color
        self._thickness = thickness
        self.set_position(x, y)
        
    def set_style(self, color: Color | AlphaColor | None = None, thickness: int | None = None):
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
    
    def set_position(self, x: int | None = None, y: int | None = None, radius: int | None = None):
        if x is not None:
            self._original_x = x
        if y is not None:
            self._original_y = y
        if radius is not None:
            self._radius = radius

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()

    def set_new_frame_size(self, frame):
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        self._x = self._frame_width + self._original_x if self._original_x < 0 else self._original_x
        self._y = self._frame_height + self._original_y if self._original_y < 0 else self._original_y
    
    def _handle_mouse(self, mouse: MouseData):
        pass

    def _render(self, frame):
        opacity = 1.0
        if isinstance(self._color, AlphaColor):
            opacity = self._color.alpha
        
        if opacity == 1.0:
            cv2.circle(frame, (self._x, self._y), self._radius, self._color, self._thickness)
        else:
            overlay = frame.copy()
            cv2.circle(overlay, (self._x, self._y), self._radius, self._color, self._thickness)
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

    def _debug_render(self, frame):
        cv2.rectangle(frame, (self._x - self._radius, self._y - self._radius), (self._x + self._radius, self._y + self._radius), (0, 255, 255, 1))
        cv2.line(frame, (self._x - 10, self._y), (self._x + 10, self._y), (0, 255, 0), 1)
        cv2.line(frame, (self._x, self._y - 10), (self._x, self._y +  10), (0, 255, 0), 1)

class CenterCross(Element):
    def __init__(self, size: int=5, color: Color | AlphaColor=Color(0, 0, 255), thickness: int=2):
        super().__init__()
        self._size = size
        self._color = color
        self._thickness = thickness
        self._x1 = -1
        self._x2 = -1
        self._y1 = -1
        self._y2 = -1
        self._center_x = -1
        self._center_y = -1
        self._original_x: int | None = None
        self._original_y: int | None = None
        self.set_position()

    def set_style(self, color: Color | AlphaColor | None = None, thickness: int | None = None, size: int | None = None):
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
        if size is not None:
            self._size = size

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()

    def set_position(self, x: int | None = None, y: int | None = None):
        if x is not None:
            self._original_x = x
        if y is not None:
            self._original_y = y

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()
        
    def set_new_frame_size(self, frame):
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        self._center_x = self._frame_width // 2 if self._original_x is None else self._resolve_x(self._original_x)
        self._center_y = self._frame_height // 2 if self._original_y is None else self._resolve_y(self._original_y)
        self._x1 = self._center_x - self._size
        self._x2 = self._center_x + self._size
        self._y1 = self._center_y - self._size
        self._y2 = self._center_y + self._size

    def _resolve_x(self, x: int) -> int:
        return self._frame_width + x if x < 0 else x

    def _resolve_y(self, y: int) -> int:
        return self._frame_height + y if y < 0 else y
    
    def _handle_mouse(self, mouse: MouseData):
        pass

    def _render(self, frame):
        opacity = 1.0
        if isinstance(self._color, AlphaColor):
            opacity = self._color.alpha
        
        if opacity == 1.0:
            cv2.line(frame, (self._x1, self._center_y), (self._x2, self._center_y), self._color, self._thickness) # Horizontal
            cv2.line(frame, (self._center_x, self._y1), (self._center_x, self._y2), self._color, self._thickness) # Veritical
        else:
            overlay = frame.copy()
            cv2.line(overlay, (self._x1, self._center_y), (self._x2, self._center_y), self._color, self._thickness) # Horizontal
            cv2.line(overlay, (self._center_x, self._y1), (self._center_x, self._y2), self._color, self._thickness) # Veritical
            cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)

    def _debug_render(self, frame):
        cv2.rectangle(frame, (self._x1, self._y1), (self._x2, self._y2), (0, 255, 255, 1))
        cv2.line(frame, (self._x1 - 10, self._center_y), (self._x2 + 10, self._center_y), (0, 255, 0), 1)
        cv2.line(frame, (self._center_x, self._y1 - 10), (self._center_x, self._y2 +  10), (0, 255, 0), 1)
    


class Outline(Container):
    def __init__(self, color: Color | AlphaColor, thickness: int = 2):
        super().__init__()
        
        self._color = color
        self._thickness = thickness
        self._points: list[Int_Vector2] = []
        self._last_num_of_points = -1
    
    def _flush(self):
        self.clear()
        for _ in range(len(self._points)):
            if isinstance(self._color, AlphaColor):
                self.add(Line(0, 0, 0, 0, AlphaColor(self._color, self._color.alpha), self._thickness))
            else:
                self.add(Line(0, 0, 0, 0, self._color, self._thickness))
    
    def set_style(self, color: Color | AlphaColor | None = None, thickness: int | None = None):
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
        for line in self._elements:
            line.set_style(color, thickness)
    
    def set_points(self, points: list[Int_Vector2]):
        self._points = points
        if len(points) != self._last_num_of_points:
            self._last_num_of_points = len(points)
            self._flush()
    
    def _render(self, frame):
        num_of_points = len(self._points)
        for i in range(num_of_points):
            pt1 = self._points[i]
            pt2 = self._points[(i + 1) % num_of_points]
            line: Line = self._elements[i]
            line.set_position(pt1.x, pt1.y, pt2.x, pt2.y)
            
        return super()._render(frame)
