import cv2
from typing import TYPE_CHECKING

from UI.elements import Text, TextStyle, Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Slider, SliderStyle, Container, Rectangle, Circle, Line
from UI.windows.Window import Window
from utils.common import create_blank_frame
from utils.models import AlphaColor, Color, Padding, ScanResult


if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class DroneWindow(Window):
    """Window for displaying state and changing drone parameters."""

    def __init__(self, window_controller: WindowController, window_name="Drone Settings"):
        """Create the drone settings window.

        Args:
            window_controller: Controller that owns this window.
            window_name: OpenCV title and controller lookup key.
        """
        super().__init__(window_controller, window_name)
        self._base_frame = create_blank_frame(600, 600)
    
    def _setup(self):
        """Create template elements."""
        # === UI variables ===
        
        
        # === UI elements ===
        
        
        # === Add elements to root ===

        
    
    def _render(self, camera_frame, scan_result: ScanResult):
        """Render the template elements.

        Args:
            camera_frame: Unused camera image supplied by the window lifecycle.
            scan_result: Unused QR result supplied by the window lifecycle.
        """
        frame = self._base_frame.copy()
        
        

        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    


