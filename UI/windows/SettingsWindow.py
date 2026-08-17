import cv2
import numpy as np
from typing import TYPE_CHECKING

from UI.elements import Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Text, Slider, Container
from UI.windows.Window import Window
from utils.Logger import logger
from utils.common import is_window_open
from utils.models import AlphaColor, Color, ScanResult

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class SettingsWindow(Window):
    def __init__(self, window_controller: WindowController, window_name="Settings"):
        super().__init__(window_controller, window_name)
        self._base_frame = np.full((600, 600, 3), 255, dtype=np.uint8)
    
    def _setup(self):
        # === UI variables ===
        self._debug_button_state = False
        
        # === UI elements ===
        self._debug_button = Button(7, 7, "---- debug render", self._debug_button_callback)
        self._validation_button = Button(7, 33, "---- validation settings", self._validation_button_callback)
        
        # === Add elements to root ===
        self._root.add(self._debug_button)
        self._root.add(self._validation_button)
        
    
    def render(self, camera_frame, scan_result: ScanResult):
        if not self._enabled:
            return
        
        if not is_window_open(self.window_name):
            self.set_enabled(False)
            return
        
        
        frame = self._base_frame.copy()
        
        self._debug_button_update()
        self._validation_button_update()
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    
    def _debug_button_update(self):
        self._debug_button.set_text(
            f"{"Hide" if self._debug_button_state else "Show"} debug renders",
            ButtonStyle(
                color=(Color(255, 255, 255) if self._debug_button_state else Color(0, 0, 0)),
                background_color=(AlphaColor(55, 65, 65) if self._debug_button_state else AlphaColor(215, 211, 209))
            )
        )
    
    def _debug_button_callback(self):
        self._debug_button_state = not self._debug_button_state
        logger.debug(f"{"Showing" if self._debug_button_state else "Hid"} debug renders")
        for window in self.controller.windows.values():
            window._root.set_debug_render(self._debug_button_state)
    
    def _validation_button_update(self):
        is_validation_settings_enabled = self.controller.windows["Validation Settings"].is_enabled
        self._validation_button.set_text(
            f"{"Close" if is_validation_settings_enabled else "Open"} validation settings",
            ButtonStyle(
                color=(Color(255, 255, 255) if is_validation_settings_enabled else Color(0, 0, 0)),
                background_color=(AlphaColor(55, 65, 65) if is_validation_settings_enabled else AlphaColor(215, 211, 209))
            )
        ) 
    
    def _validation_button_callback(self):
        validationSettingsWindow = self.controller.windows["Validation Settings"]
        validationSettingsWindow.set_enabled(not validationSettingsWindow.is_enabled)


