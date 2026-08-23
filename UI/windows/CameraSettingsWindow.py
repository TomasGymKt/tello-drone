import cv2
import numpy as np
from typing import TYPE_CHECKING

from UI.elements import Text, Slider, SliderStyle, Line
from UI.windows.Window import Window
from utils.Logger import logger
from utils.common import create_blank_frame
from utils.models import AlphaColor, Color, ScanResult
from settings import settings

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class CameraSettingsWindow(Window):
    def __init__(self, window_controller: WindowController, window_name="Camera Settings"):
        super().__init__(window_controller, window_name)
        self._base_frame = create_blank_frame(600, 600)
    
    def _setup(self):
        # === UI variables ===
        
        # === UI elements ===
        self._focal_label_text = Text(7, 7, "Focal lenght:")
        self._focal_slider = Slider(7, 41, 0, 2500, settings.camera_focal_length, self._focal_callback, SliderStyle(width=500))
        self._focal_value_text = Text(520, 33, "----")
        
        
        self._qr_label_text = Text(7, 70, "QR Code size (cm):")
        self._qr_slider = Slider(7, 104, 0, 50, settings.qr_code_size_cm, self._qr_callback, SliderStyle(width=500))
        self._qr_value_text = Text(520, 96, "----")
        
        # === Add elements to root ===
        self._root.add(self._focal_label_text)
        self._root.add(self._focal_slider)
        self._root.add(self._focal_value_text)
        
        
        self._root.add(self._qr_label_text)
        self._root.add(self._qr_slider)
        self._root.add(self._qr_value_text)

    def _render(self, camera_frame, scan_result: ScanResult):
        frame = self._base_frame.copy()
        
        self._focal_value_text.set_text(f"{settings.camera_focal_length:.0f}")
        self._qr_value_text.set_text(f"{settings.qr_code_size_cm:.1f}")
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    def _focal_callback(self, value: float):
        settings.camera_focal_length = round(value)

    def _qr_callback(self, value: float):
        settings.qr_code_size_cm = round(value, 1)

