from dataclasses import dataclass
from typing import Callable

import cv2

from UI.elements.Element import Element
from utils.common import is_mouse_in_bounding_box
from utils.models import Color, MouseData


@dataclass(slots=True)
class SliderStyle:
    """Colors and dimensions used to draw a slider."""
    color_left: Color = Color(255, 117, 0)
    color_right: Color = Color(239, 239, 239)
    handle_color: Color = color_left
    width: int = 200
    height: int = 6
    handle_radius: int = 8
    handle_thickness: int = -1


class Slider(Element):
    """Interactive slider that maps pointer position to a numeric range."""
    def __init__(
        self,
        x: int,
        y: int,
        min_value: float,
        max_value: float,
        value: float,
        callback: Callable[[float], None] | None = None,
        style: SliderStyle = SliderStyle(),
    ):
        """Create a slider.

        Args:
            x: Left edge, or right offset when negative.
            y: Top edge, or bottom offset when negative.
            min_value: Smallest selectable value.
            max_value: Largest selectable value.
            value: Initial value, clamped to the selectable range.
            callback: Optional function called after the value changes.
            style: Colors and dimensions used to render the slider.

        Raises:
            ValueError: If min_value exceeds max_value.
        """
        super().__init__()
        if min_value > max_value:
            raise ValueError("min_value cannot be greater than max_value")

        self._original_x = 0
        self._original_y = 0

        self._x1 = -1
        self._y1 = -1
        self._x2 = -1
        self._y2 = -1

        self._handle_x = -1
        self._handle_y = -1

        self._min_value = min_value
        self._max_value = max_value
        self._value = value
        self._style = style
        self._callback = callback

        self.is_hovered = False
        self.is_pressed = False

        self.set_value(value)
        self.set_position(x, y)

    @property
    def value(self) -> float:
        """Return the slider's current value.

        Returns:
            Current value within the configured range.
        """
        return self._value

    @property
    def min_value(self) -> float:
        """Return the smallest selectable value.

        Returns:
            Configured minimum value.
        """
        return self._min_value

    @property
    def max_value(self) -> float:
        """Return the largest selectable value.

        Returns:
            Configured maximum value.
        """
        return self._max_value

    def set_value(self, value: float):
        """Clamp and set the slider value.

        Args:
            value: Requested value within or outside the selectable range.
        """
        value = max(self._min_value, min(value, self._max_value))

        if value == self._value:
            return

        self._value = value

        if self._callback is not None:
            self._callback(value)

    def set_style(self, style: SliderStyle):
        """Replace slider colors and dimensions, then recompute layout.

        Args:
            style: New slider rendering configuration.
        """
        self._style = style
        self.set_position()

    def set_position(self, x: int | None = None, y: int | None = None):
        """Update the slider's source position and resolve it against the frame.

        Args:
            x: New left edge, or right offset when negative.
            y: New top edge, or bottom offset when negative.
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
        """Update layout bounds and resolve the slider position.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        self.set_position()

    def _resolve_position(self):
        """Resolve source coordinates into track and handle bounds."""
        self._x1 = self._original_x
        self._y1 = self._original_y

        if self._original_x < 0:
            self._x1 = self._frame_width + self._original_x - self._style.width

        if self._original_y < 0:
            self._y1 = self._frame_height + self._original_y - self._style.height

        self._x2 = self._x1 + self._style.width
        self._y2 = self._y1 + self._style.height

        self._update_handle_position()

    def _update_handle_position(self):
        """Place the handle according to the current normalized value."""
        if self._max_value == self._min_value:
            normalized = 0.0
        else:
            normalized = (
                (self._value - self._min_value)
                / (self._max_value - self._min_value)
            )

        self._handle_x = round(
            self._x1 + normalized * self._style.width
        )

        self._handle_y = self._y1 + self._style.height // 2

    def _value_from_mouse(self, mouse: MouseData) -> float:
        """Convert a pointer position into a clamped slider value.

        Args:
            mouse: Pointer coordinates to convert.

        Returns:
            Value corresponding to the pointer's horizontal position.
        """
        normalized = (mouse.x - self._x1) / self._style.width
        normalized = max(0.0, min(normalized, 1.0))

        return self._min_value + normalized * (
            self._max_value - self._min_value
        )

    def _handle_mouse(self, mouse: MouseData):
        """Update interaction state and value from a mouse event.

        Args:
            mouse: Event type and pointer coordinates to process.
        """
        self.is_hovered = is_mouse_in_bounding_box(
            mouse,
            self._x1 - self._style.handle_radius,
            self._y1 - self._style.handle_radius,
            self._x2 + self._style.handle_radius,
            self._y2 + self._style.handle_radius,
        )

        if mouse.event == cv2.EVENT_LBUTTONDOWN or mouse.event == cv2.EVENT_LBUTTONDBLCLK:
            if self.is_hovered:
                self.is_pressed = True
                self.set_value(self._value_from_mouse(mouse))

        elif mouse.event == cv2.EVENT_MOUSEMOVE:
            if self.is_pressed:
                self.set_value(self._value_from_mouse(mouse))

        elif mouse.event == cv2.EVENT_LBUTTONUP:
            self.is_pressed = False

    def _render(self, frame):
        """Draw the filled track, remaining track, and handle.

        Args:
            frame: OpenCV image that receives the slider drawing.
        """
        self._update_handle_position()

        center_y = self._y1 + self._style.height // 2

        cv2.line(
            frame,
            (self._x1, center_y),
            (self._handle_x, center_y),
            self._style.color_left,
            self._style.height,
        )

        cv2.line(
            frame,
            (self._handle_x, center_y),
            (self._x2, center_y),
            self._style.color_right,
            self._style.height,
        )

        cv2.circle(
            frame,
            (self._handle_x, self._handle_y),
            self._style.handle_radius,
            self._style.handle_color,
            self._style.handle_thickness,
        )

    def _debug_render(self, frame):
        """Draw resolved bounds and handle guides.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))

        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))

        cv2.line(frame, (self._handle_x - 25, self._handle_y), (self._handle_x + 25, self._handle_y), (0, 255, 0), 1)
        cv2.line(frame, (self._handle_x, self._handle_y - 25), (self._handle_x, self._handle_y + 25), (0, 255, 0), 1)
