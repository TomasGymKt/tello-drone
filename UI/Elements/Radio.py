from dataclasses import dataclass
from typing import Callable

import cv2

from UI.elements.Element import Element
from UI.elements.Shapes import Rectangle
from utils.common import get_elements_bounding_box, is_mouse_in_bounding_box
from utils.models import AlphaColor, Color, Padding, MouseData


@dataclass(slots=True)
class RadioStyle:
    """Colors, typography, and geometry used to draw a radio option."""
    color: Color = Color(239, 239, 239)
    selected_color: Color = Color(255, 192, 128)
    background_color: AlphaColor = AlphaColor(0, 0, 0, 0.8)
    padding: Padding = Padding(5)
    radius: int = 8
    circle_thickness: int = 2
    circle_text_gap: int = 5
    fontSize: float = 0.6
    fontThickness: int = 1


class Radio:
    """Selectable option managed by a RadioGroup."""

    def __init__(self, x: int, y: int, text: str, value, style: RadioStyle = RadioStyle()):
        """Create a radio option.

        Args:
            x: Left edge, or right offset when negative.
            y: Top edge, or bottom offset when negative.
            text: Label to draw beside the radio circle.
            value: Value reported by the owning group when selected.
            style: Colors, typography, and geometry to apply.
        """
        self._original_x = 0
        self._original_y = 0

        self._x1 = -1
        self._y1 = -1
        self._x2 = -1
        self._y2 = -1

        self._circle_x = -1
        self._circle_y = -1

        self._set_frame_size_on_render = True
        self._show_debug_render = False
        self._frame_width = -1
        self._frame_height = -1

        self._text = text
        self._value = value
        self._group: RadioGroup | None = None
        self._style = style

        self.is_hovered = False
        self.is_pressed = False

        self._calculate_text_size()
        self.set_position(x, y)

    @property
    def selected(self) -> bool:
        """Return whether this option is selected by its owning group.

        Returns:
            True when this option is currently selected.
        """
        return self._group.selected is self

    def _calculate_text_size(self):
        """Measure the label using the current font style."""
        (self._text_width, self._text_height), _ = cv2.getTextSize(
            self._text,
            cv2.FONT_HERSHEY_SIMPLEX,
            self._style.fontSize,
            self._style.fontThickness,
        )

    def set_text(self, text: str, style: RadioStyle | None = None):
        """Update label content and optionally replace its style.

        Args:
            text: New label content.
            style: Replacement style; the current style is retained when omitted.
        """
        if style is None:
            style = self._style

        self._text = text
        self._style = style

        self._calculate_text_size()
        self.set_position()
    
    def set_position(self, x: int | None = None, y: int | None = None):
        """Update the option's source position and resolve it against the frame.

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

    def set_style(self, style: RadioStyle):
        """Replace the radio style and recompute its layout.

        Args:
            style: Colors, typography, and geometry to apply.
        """
        self._style = style

        self._calculate_text_size()
        self.set_position()

    def set_new_frame_size(self, frame):
        """Update layout bounds and resolve the option position.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        self._frame_height, self._frame_width = frame.shape[:2]
        self._set_frame_size_on_render = False
        self.set_position()

    def _request_layout(self):
        """Mark the option for layout during its next render."""
        self._set_frame_size_on_render = True

    def _resolve_position(self):
        """Resolve source coordinates into label and circle bounds."""
        content_height = max(self._style.radius * 2, self._text_height)

        width = (self._text_width + self._style.radius * 2 + self._style.circle_text_gap + self._style.padding.horizontal)

        height = content_height + self._style.padding.vertical

        self._x1 = self._original_x
        self._y1 = self._original_y

        if self._original_x < 0:
            self._x1 = self._frame_width + self._original_x - width

        if self._original_y < 0:
            self._y1 = self._frame_height + self._original_y - height

        self._x2 = self._x1 + width
        self._y2 = self._y1 + height

        self._circle_x = self._x1 + self._style.padding.left + self._style.radius
        self._circle_y = self._y1 + self._style.padding.top + content_height // 2

    def handle_mouse(self, mouse: MouseData):
        """Update interaction state and select the option after a click.

        Args:
            mouse: Event type and pointer coordinates to process.
        """
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
        """Lay out and draw the radio option.

        Args:
            frame: OpenCV image that receives the option drawing.
        """
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
        """Enable or disable the option's debug overlay.

        Args:
            enabled: Whether debug geometry should be visible.
        """
        self._show_debug_render = enabled

    def _debug_render(self, frame):
        """Draw resolved bounds and circle guides.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        cv2.circle(frame, (self._x1, self._y1), 3, (0, 0, 255))
        cv2.circle(frame, (self._x1, self._y1), 12, (0, 0, 255))

        cv2.circle(frame, (self._x2, self._y2), 3, (255, 0, 0))
        cv2.circle(frame, (self._x2, self._y2), 12, (255, 0, 0))

        cv2.line(frame, (self._circle_x - 25, self._circle_y), (self._circle_x + 25, self._circle_y), (0, 255, 0), 1)
        cv2.line(frame, (self._circle_x, self._circle_y - 25), (self._circle_x, self._circle_y + 25), (0, 255, 0), 1)
    

class RadioGroup(Element):
    """Coordinates a mutually exclusive collection of radio options."""

    def __init__(self, callback: Callable[[object], None] | None = None):
        """Create an empty radio group.

        Args:
            callback: Optional function called with the selected option's value.
        """
        super().__init__()
        self._radios: list[Radio] = []
        self._selected: Radio | None = None
        self._callback = callback

    @property
    def selected(self) -> Radio | None:
        """Return the selected option, if any.

        Returns:
            Selected radio option or None when no option is selected.
        """
        return self._selected

    @property
    def value(self):
        """Return the selected option's value.

        Returns:
            Selected value, or None when no option is selected.
        """
        return None if self._selected is None else self._selected._value
    
    @property
    def radios(self) -> list[Radio]:
        """Return the group's radio options.

        Returns:
            Mutable list of radio options in render order.
        """
        return self._radios

    def add(self, radio: Radio):
        """Add an unowned option to the group.

        Args:
            radio: Radio option to manage.

        Raises:
            ValueError: If the option already belongs to a group.
        """
        if radio._group is not None:
            raise ValueError("Radio already belongs to a RadioGroup")
        
        radio._group = self
        radio.set_debug_render(self._show_debug_render)
        self._radios.append(radio)

    def select(self, radio: Radio):
        """Select an option and notify the group callback.

        Args:
            radio: Managed radio option to select.
        """
        self._selected = radio

        if self._callback is not None:
            self._callback(radio._value)

    def _handle_mouse(self, mouse: MouseData):
        """Forward a mouse event to every radio option.

        Args:
            mouse: Event type and pointer coordinates to forward.
        """
        for radio in self._radios:
            radio.handle_mouse(mouse)

    def set_new_frame_size(self, frame):
        """Update layout bounds for every managed radio option.

        Args:
            frame: OpenCV image whose dimensions define layout bounds.
        """
        super().set_new_frame_size(frame)
        for radio in self._radios:
            radio.set_new_frame_size(frame)

    def _render(self, frame):
        """Draw every managed radio option.

        Args:
            frame: OpenCV image that receives the option drawings.
        """
        for radio in self._radios:
            radio.render(frame)

    def set_debug_render(self, enabled: bool):
        """Set debug rendering for the group and all options.

        Args:
            enabled: Whether debug geometry should be visible.
        """
        super().set_debug_render(enabled)
        for radio in self._radios:
            radio.set_debug_render(enabled)

    def set_style(self, *args, **kwargs):
        """Reject style updates because options have independent styles.

        Raises:
            NotImplementedError: Always, because the group has no shared style.
        """
        raise NotImplementedError("RadioGroup does not have a shared style")

    def set_position(self, *args, **kwargs):
        """Reject position updates because options have independent positions.

        Raises:
            NotImplementedError: Always, because the group has no shared position.
        """
        raise NotImplementedError("RadioGroup does not have a shared position")
    
    def _debug_render(self, frame):
        """Draw a bounding box around all managed radio options.

        Args:
            frame: OpenCV image that receives the debug drawing.
        """
        box = get_elements_bounding_box(self._radios, include_nested=False)
        if box is None:
            return
        x1, y1, x2, y2 = box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 1)
