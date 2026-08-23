import cv2

from UI.elements.Container import Container
from UI.elements.Element import Element
from utils.models import Color, AlphaColor, Int_Vector2, MouseData

class Line(Element):
    """Line segment with frame-relative endpoint support."""

    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: Color | AlphaColor, thickness: int = 1):
        """Create a line segment.

        Args:
            x1: First endpoint x-coordinate, or right offset when negative.
            y1: First endpoint y-coordinate, or bottom offset when negative.
            x2: Second endpoint x-coordinate, or right offset when negative.
            y2: Second endpoint y-coordinate, or bottom offset when negative.
            color: BGR line color, optionally with alpha.
            thickness: OpenCV line thickness.
        """
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
        """Update line color and/or thickness.

        Args:
            color: Replacement BGR color, optionally with alpha.
            thickness: Replacement OpenCV line thickness.
        """
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
    
    def set_position(self, x1: int | None = None, y1: int | None = None, x2: int | None = None, y2: int | None = None):
        """Update line endpoints and resolve negative coordinates.

        Args:
            x1: First endpoint x-coordinate, or right offset when negative.
            y1: First endpoint y-coordinate, or bottom offset when negative.
            x2: Second endpoint x-coordinate, or right offset when negative.
            y2: Second endpoint y-coordinate, or bottom offset when negative.
        """
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
        """Update layout bounds and resolve line endpoints.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        """Resolve all source endpoints against the current frame."""
        self._x1 = self._resolve_x(self._original_x1)
        self._y1 = self._resolve_y(self._original_y1)
        self._x2 = self._resolve_x(self._original_x2)
        self._y2 = self._resolve_y(self._original_y2)

    def _resolve_x(self, x: int) -> int:
        """Resolve an x-coordinate against the current frame width.

        Args:
            x: Source x-coordinate, possibly a negative right offset.

        Returns:
            Absolute x-coordinate in the current frame.
        """
        return self._frame_width + x if x < 0 else x

    def _resolve_y(self, y: int) -> int:
        """Resolve a y-coordinate against the current frame height.

        Args:
            y: Source y-coordinate, possibly a negative bottom offset.

        Returns:
            Absolute y-coordinate in the current frame.
        """
        return self._frame_height + y if y < 0 else y
    
    def _handle_mouse(self, mouse: MouseData):
        """Ignore mouse events because lines are not interactive.

        Args:
            mouse: Event type and pointer coordinates to ignore.
        """
        pass

    def _render(self, frame):
        """Draw the line, blending through an overlay when translucent.

        Args:
            frame: OpenCV image that receives the line drawing.
        """
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
        """Draw markers at both resolved endpoints.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
    


class Rectangle(Element):
    """Rectangle with frame-relative corner support."""

    def __init__(self, x1: int, y1: int, x2: int, y2: int, color: Color | AlphaColor, thickness: int = -1):
        """Create a rectangle.

        Args:
            x1: First corner x-coordinate, or right offset when negative.
            y1: First corner y-coordinate, or bottom offset when negative.
            x2: Second corner x-coordinate, or right offset when negative.
            y2: Second corner y-coordinate, or bottom offset when negative.
            color: BGR rectangle color, optionally with alpha.
            thickness: OpenCV border thickness; -1 fills the rectangle.
        """
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
        """Update rectangle color and/or thickness.

        Args:
            color: Replacement BGR color, optionally with alpha.
            thickness: Replacement border thickness; -1 fills the rectangle.
        """
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness

    def set_position(self, x1: int | None = None, y1: int | None = None, x2: int | None = None, y2: int | None = None):
        """Update rectangle corners and resolve negative coordinates.

        Args:
            x1: First corner x-coordinate, or right offset when negative.
            y1: First corner y-coordinate, or bottom offset when negative.
            x2: Second corner x-coordinate, or right offset when negative.
            y2: Second corner y-coordinate, or bottom offset when negative.
        """
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
        """Update layout bounds and resolve rectangle corners.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        """Resolve all source corners against the current frame."""
        self._x1 = self._frame_width + self._original_x1 if self._original_x1 < 0 else self._original_x1
        self._y1 = self._frame_height + self._original_y1 if self._original_y1 < 0 else self._original_y1
        self._x2 = self._frame_width + self._original_x2 if self._original_x2 < 0 else self._original_x2
        self._y2 = self._frame_height + self._original_y2 if self._original_y2 < 0 else self._original_y2
    
    def _handle_mouse(self, mouse: MouseData):
        """Ignore mouse events because rectangles are not interactive.

        Args:
            mouse: Event type and pointer coordinates to ignore.
        """
        pass

    def _render(self, frame):
        """Draw the rectangle, blending through an overlay when translucent.

        Args:
            frame: OpenCV image that receives the rectangle drawing.
        """
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
        """Draw markers at both resolved corners.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))
        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))
    

class Circle(Element):
    """Circle with frame-relative center support."""

    def __init__(self, x: int, y: int, radius: int, color: Color | AlphaColor, thickness: int = -1):
        """Create a circle.

        Args:
            x: Center x-coordinate, or right offset when negative.
            y: Center y-coordinate, or bottom offset when negative.
            radius: Circle radius in pixels.
            color: BGR circle color, optionally with alpha.
            thickness: OpenCV border thickness; -1 fills the circle.
        """
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
        """Update circle color and/or thickness.

        Args:
            color: Replacement BGR color, optionally with alpha.
            thickness: Replacement border thickness; -1 fills the circle.
        """
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
    
    def set_position(self, x: int | None = None, y: int | None = None, radius: int | None = None):
        """Update center and/or radius, resolving negative coordinates.

        Args:
            x: Center x-coordinate, or right offset when negative.
            y: Center y-coordinate, or bottom offset when negative.
            radius: Replacement radius in pixels.
        """
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
        """Update layout bounds and resolve the circle center.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        """Resolve the source center against the current frame."""
        self._x = self._frame_width + self._original_x if self._original_x < 0 else self._original_x
        self._y = self._frame_height + self._original_y if self._original_y < 0 else self._original_y
    
    def _handle_mouse(self, mouse: MouseData):
        """Ignore mouse events because circles are not interactive.

        Args:
            mouse: Event type and pointer coordinates to ignore.
        """
        pass

    def _render(self, frame):
        """Draw the circle, blending through an overlay when translucent.

        Args:
            frame: OpenCV image that receives the circle drawing.
        """
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
        """Draw the circle bounds and center guides.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        cv2.rectangle(frame, (self._x - self._radius, self._y - self._radius), (self._x + self._radius, self._y + self._radius), (0, 255, 255, 1))
        cv2.line(frame, (self._x - 10, self._y), (self._x + 10, self._y), (0, 255, 0), 1)
        cv2.line(frame, (self._x, self._y - 10), (self._x, self._y +  10), (0, 255, 0), 1)

class CenterCross(Element):
    """Crosshair centered in the frame or at an explicit position."""

    def __init__(self, size: int=5, color: Color | AlphaColor=Color(0, 0, 255), thickness: int=2):
        """Create a centered crosshair.

        Args:
            size: Half-length of each crosshair arm in pixels.
            color: BGR crosshair color, optionally with alpha.
            thickness: OpenCV line thickness.
        """
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
        """Update crosshair color, thickness, and/or arm size.

        Args:
            color: Replacement BGR color, optionally with alpha.
            thickness: Replacement line thickness.
            size: Replacement half-length of each arm.
        """
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
        """Set an explicit center or keep the crosshair frame-centered.

        Args:
            x: Center x-coordinate, or right offset when negative.
            y: Center y-coordinate, or bottom offset when negative.
        """
        if x is not None:
            self._original_x = x
        if y is not None:
            self._original_y = y

        if self._frame_width > 0 and self._frame_height > 0:
            self._resolve_position()
        else:
            self._request_layout()
        
    def set_new_frame_size(self, frame):
        """Update layout bounds and resolve the crosshair center.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        """Resolve the configured or frame-centered crosshair position."""
        self._center_x = self._frame_width // 2 if self._original_x is None else self._resolve_x(self._original_x)
        self._center_y = self._frame_height // 2 if self._original_y is None else self._resolve_y(self._original_y)
        self._x1 = self._center_x - self._size
        self._x2 = self._center_x + self._size
        self._y1 = self._center_y - self._size
        self._y2 = self._center_y + self._size

    def _resolve_x(self, x: int) -> int:
        """Resolve an x-coordinate against the current frame width.

        Args:
            x: Source x-coordinate, possibly a negative right offset.

        Returns:
            Absolute x-coordinate in the current frame.
        """
        return self._frame_width + x if x < 0 else x

    def _resolve_y(self, y: int) -> int:
        """Resolve a y-coordinate against the current frame height.

        Args:
            y: Source y-coordinate, possibly a negative bottom offset.

        Returns:
            Absolute y-coordinate in the current frame.
        """
        return self._frame_height + y if y < 0 else y
    
    def _handle_mouse(self, mouse: MouseData):
        """Ignore mouse events because crosshairs are not interactive.

        Args:
            mouse: Event type and pointer coordinates to ignore.
        """
        pass

    def _render(self, frame):
        """Draw the horizontal and vertical crosshair arms.

        Args:
            frame: OpenCV image that receives the crosshair drawing.
        """
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
        """Draw the crosshair bounds and center guides.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        cv2.rectangle(frame, (self._x1, self._y1), (self._x2, self._y2), (0, 255, 255, 1))
        cv2.line(frame, (self._x1 - 10, self._center_y), (self._x2 + 10, self._center_y), (0, 255, 0), 1)
        cv2.line(frame, (self._center_x, self._y1 - 10), (self._center_x, self._y2 +  10), (0, 255, 0), 1)
    


class Outline(Container):
    """Closed polygon outline backed by one line element per edge."""

    def __init__(self, color: Color | AlphaColor, thickness: int = 2):
        """Create an empty polygon outline.

        Args:
            color: BGR outline color, optionally with alpha.
            thickness: OpenCV line thickness for each edge.
        """
        super().__init__()
        
        self._color = color
        self._thickness = thickness
        self._points: list[Int_Vector2] = []
        self._last_num_of_points = -1
    
    def _flush(self):
        """Rebuild line children to match the current point count."""
        self.clear()
        for _ in range(len(self._points)):
            if isinstance(self._color, AlphaColor):
                self.add(Line(0, 0, 0, 0, AlphaColor(self._color, self._color.alpha), self._thickness))
            else:
                self.add(Line(0, 0, 0, 0, self._color, self._thickness))
    
    def set_style(self, color: Color | AlphaColor | None = None, thickness: int | None = None):
        """Update the style of every outline edge.

        Args:
            color: Replacement BGR color, optionally with alpha.
            thickness: Replacement line thickness.
        """
        if color is not None:
            self._color = color
        if thickness is not None:
            self._thickness = thickness
        for line in self._elements:
            line.set_style(color, thickness)
    
    def set_points(self, points: list[Int_Vector2]):
        """Replace polygon vertices and rebuild edges when the count changes.

        Args:
            points: Ordered polygon vertices; the last vertex connects to the first.
        """
        self._points = points
        if len(points) != self._last_num_of_points:
            self._last_num_of_points = len(points)
            self._flush()
    
    def _render(self, frame):
        """Update edge endpoints from polygon vertices and render them.

        Args:
            frame: OpenCV image that receives the outline drawing.
        """
        num_of_points = len(self._points)
        for i in range(num_of_points):
            pt1 = self._points[i]
            pt2 = self._points[(i + 1) % num_of_points]
            line: Line = self._elements[i]
            line.set_position(pt1.x, pt1.y, pt2.x, pt2.y)
            
        return super()._render(frame)
