from __future__ import annotations
import cv2
import numpy as np
from typing import TYPE_CHECKING

from UI.elements import Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Text, Slider, Container
from UI.windows.Window import Window
from utils.Logger import logger
from utils.common import create_blank_frame
from utils.models import AlphaColor, Color, ScanResult

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class SettingsWindow(Window):
    """Menu window for debug rendering and secondary settings windows."""

    def __init__(self, window_controller: WindowController, window_name="Settings"):
        """Create the settings-menu window.

        Args:
            window_controller: Controller that owns this window.
            window_name: OpenCV title and controller lookup key.
        """
        super().__init__(window_controller, window_name)
        self._base_frame = create_blank_frame(600, 600)
    
    def _setup(self):
        """Create debug and settings-window toggle buttons."""
        # === UI variables ===
        self._debug_button_state = False
        
        # === UI elements ===
        self._debug_button = Button(7, 7, "---- debug render", self._debug_button_callback)
        self._validation_button = Button(7, 33, "---- validation settings", self._validation_button_callback)
        self._camera_button = Button(7, 59, "---- camera settings", self._camera_button_callback)
        self._fly_button = Button(7, 85, "---- fly contols", self._fly_button_callback)
        self._drone_button = Button(7, 111, "---- drone settings", self._drone_button_callback)
        
        # === Add elements to root ===
        self._root.add(self._debug_button)
        self._root.add(self._validation_button)
        self._root.add(self._camera_button)
        self._root.add(self._fly_button)
        self._root.add(self._drone_button)
    
    def _render(self, camera_frame, scan_result: ScanResult):
        """Render the current settings menu state.

        Args:
            camera_frame: Unused camera image supplied by the window lifecycle.
            scan_result: Unused QR result supplied by the window lifecycle.
        """
        frame = self._base_frame.copy()
        
        self._debug_button_update()
        self._validation_button_update()
        self._camera_button_update()
        self._fly_button_update()
        self._drone_button_update()
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    def _toggle_window(self, window_name: str):
        window = self.controller.windows[window_name]
        window.set_enabled(not window.is_enabled)
    
    def _update_button(self, window_name: str, button: Button, text: str):
        is_window_enabled = self.controller.windows[window_name].is_enabled
        button.set_text(
            f"{"Close" if is_window_enabled else "Open"} {text}",
            ButtonStyle(
                color=(Color(255, 255, 255) if is_window_enabled else Color(0, 0, 0)),
                background_color=(AlphaColor(55, 65, 65) if is_window_enabled else AlphaColor(215, 211, 209))
            )
        ) 
    
    def _debug_button_update(self):
        """Reflect debug-overlay visibility in the debug toggle label."""
        self._debug_button.set_text(
            f"{"Hide" if self._debug_button_state else "Show"} debug renders",
            ButtonStyle(
                color=(Color(255, 255, 255) if self._debug_button_state else Color(0, 0, 0)),
                background_color=(AlphaColor(55, 65, 65) if self._debug_button_state else AlphaColor(215, 211, 209))
            )
        )
    
    def _debug_button_callback(self):
        """Toggle debug overlays for every registered window."""
        self._debug_button_state = not self._debug_button_state
        logger.debug(f"{"Showing" if self._debug_button_state else "Hid"} debug renders")
        for window in self.controller.windows.values():
            window._root.set_debug_render(self._debug_button_state)
    
    def _validation_button_update(self):
        """Reflect the validation-settings window state in its button."""
        self._update_button("Validation Settings", self._validation_button, "validation settings")
    
    def _validation_button_callback(self):
        """Toggle the validation-settings window."""
        self._toggle_window("Validation Settings")
        
    def _camera_button_update(self):
        """Reflect the camera-settings window state in its button."""
        self._update_button("Camera Settings", self._camera_button, "camera settings")
    
    def _camera_button_callback(self):
        """Toggle the camera-settings window."""
        self._toggle_window("Camera Settings")
        
    def _fly_button_update(self):
        """Reflect the fly-controls window state in its button."""
        self._update_button("Fly Controls", self._fly_button, "fly controls")
    
    def _fly_button_callback(self):
        """Toggle the fly-controls window."""
        self._toggle_window("Fly Controls")
        
    def _drone_button_update(self):
        """Reflect the drone window state in its button."""
        self._update_button("Drone Settings", self._drone_button, "drone settings")
    
    def _drone_button_callback(self):
        """Toggle the drone window."""
        self._toggle_window("Drone Settings")
    
    


