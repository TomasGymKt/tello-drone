import cv2
from typing import TYPE_CHECKING

from UI.elements import Text, TextStyle, Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Slider, SliderStyle, Container, Rectangle, Circle, Line
from UI.windows.Window import Window
from utils.common import create_blank_frame
from utils.models import AlphaColor, Color, Padding, ScanResult

import time
from utils.color import generate_colors

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class TemplateWindow(Window):
    """Template window."""

    def __init__(self, window_controller: WindowController, window_name="Template window"):
        """Create the template window.

        Args:
            window_controller: Controller that owns this window.
            window_name: OpenCV title and controller lookup key.
        """
        super().__init__(window_controller, window_name)
        self._base_frame = create_blank_frame(300, 200)
    
    def _setup(self):
        """Create template elements."""
        # === UI variables ===
        self._max_colors = 8
        self._colors = generate_colors(self._max_colors)
        self._color_index = 0
        
        
        # === UI elements ===
        self._time_text = Text(15, 10, "Time: --:--:-- --.--.----")
        self._button = Button(90, 75, "Template", self._button_callback, ButtonStyle(padding=Padding(18)))
        
        
        # === Add elements to root ===
        self._root.add(self._time_text) # If you don't add the elements to _root they are NOT going to be rendered
        self._root.add(self._button)
        
    
    def _render(self, camera_frame, scan_result: ScanResult):
        """Render the template elements.

        Args:
            camera_frame: Unused camera image supplied by the window lifecycle.
            scan_result: Unused QR result supplied by the window lifecycle.
        """
        frame = self._base_frame.copy()
        
        self._time_text.set_text(f"Time: {time.strftime("%H:%M:%S %d.%m.%Y")}")

        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    def _button_callback(self):
        self._button.set_style(
            ButtonStyle(
                color=Color(0, 0, 0),
                background_color=AlphaColor(self._colors[self._color_index]),
                padding=Padding(18),
            )
        )
        self._color_index = (self._color_index + 1) % self._max_colors
    


