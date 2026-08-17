import time
import cv2
from typing import TYPE_CHECKING

from UI.elements import Container, Text, TextStyle, CenterCross, QRCodePloter, Button, Outline, ButtonStyle
from UI.windows.Window import Window
from config import DRAW_GHOST_QR_CODE, DRAW_REJECTED_QR_CODES
from utils.PerformanceDisplay import PerformanceDisplay
from utils.common import is_window_open
from utils.models import Color, AlphaColor, ScanResult
from utils.qr_validation import debug_is_plausible_qr_code

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController


class CameraWindow(Window):
    def __init__(self, window_controller: WindowController, window_name="Camera"):
        super().__init__(window_controller, window_name, enabled_by_default=True)

    def _setup(self):
        # === UI variables ===
        self._last_found_result: ScanResult = ScanResult()
        
        # === UI elements ===
        self._qr_ploter = QRCodePloter()
        self._performance_display = PerformanceDisplay()
        self._found_text = Text(-7, 7, f"----------", TextStyle(Color(0, 0, 255)))
        self._settings_button = Button(-7, -7, "---- settings", self._settings_button_callback)
        # self._ghost_qr_ploter = QRCodePloter()
        
        # === Add elements to root ===
        self._root.add(self._qr_ploter)
        self._root.add(self._performance_display.container)
        self._root.add(self._found_text)
        self._root.add(self._settings_button)
        self._root.add(CenterCross())
        # self._root.add(self._ghost_qr_ploter)
        self._rejected_setup()
    
    def render(self, camera_frame, scan_result: ScanResult):
        if not self._enabled:
            return
        if not is_window_open(self.window_name):
            self._window_handle()
        
        frame = camera_frame.copy()
        
        # if DRAW_GHOST_QR_CODE and self._last_found_result is not None:
        #     opacity = 0.4-(time.perf_counter()-self._last_found_result.last_scan_finished_at)*1.5
        #     if opacity > 0:
        #         self._ghost_qr_ploter.set_scan_result(self._last_found_result)
        
        self._rejected_update(scan_result)
        
        self._qr_ploter.set_scan_result(scan_result)
        
        if scan_result.success:
            self._found_text.set_text(f"Method: {scan_result.scan_method}", TextStyle(Color(0, 255, 0)))
            self._last_found_result = scan_result
        else:
            self._found_text.set_text("Not Found", TextStyle(Color(0, 0, 255)))
        
        self._settings_button_update()
        self._performance_display.update(scan_result)
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    
    def _rejected_setup(self, max_amount: int = 3):
        self._rejected_amount = max_amount
        self._rejected_outlines = [Outline(AlphaColor(0, 0, 255, 0.4), 1) for _ in range(max_amount)]
        self._rejected_times = [-1 for _ in range(max_amount)]
        self._rejected_index = 0
        
        for i in range(self._rejected_amount):
            self._root.add(self._rejected_outlines[i])
    
    def _rejected_update(self, scan_result: ScanResult, start_opacity: float = 0.4, fading_mult: float = 1.2):
        if DRAW_REJECTED_QR_CODES and not scan_result.success and scan_result.qr_code is not None:
            outline = self._rejected_outlines[self._rejected_index]
            self._rejected_times[self._rejected_index] = time.perf_counter()
            self._rejected_index = (self._rejected_index + 1) % self._rejected_amount
            
            outline.visible = True
            outline.set_points(scan_result.qr_code.points)
        
        for i in range(self._rejected_amount):
            opacity = start_opacity - (time.perf_counter() - self._rejected_times[i]) * fading_mult
            self._rejected_outlines[i].set_style(AlphaColor(0, 0, 255, opacity))
            if opacity < 0:
                self._rejected_outlines[i].visible = False
    
    def _settings_button_update(self):
        is_settings_enabled = self.controller.windows["Settings"].is_enabled
        self._settings_button.set_text(
            f"{"Close" if is_settings_enabled else "Open"} settings",
            ButtonStyle(
                color=(Color(255, 255, 255) if is_settings_enabled else Color(0, 0, 0)),
                background_color=(AlphaColor(55, 65, 65) if is_settings_enabled else AlphaColor(235, 231, 229))
            )
        ) 
    
    def _settings_button_callback(self):
        settingsWindow = self.controller.windows["Settings"]
        settingsWindow.set_enabled(not settingsWindow.is_enabled)
