from UI.windows.CameraWindow import CameraWindow
from UI.windows.SettingsWindow import SettingsWindow
from UI.windows.ValidationSettingsWindow import ValidationSettingsWindow
from UI.windows.CameraSettingsWindow import CameraSettingsWindow
from UI.windows.Window import Window
from utils.models import ScanResult

class WindowController:
    def __init__(self):
        self._windows: dict[str, Window] = {}
        
        self.add_window( CameraWindow(self) )
        self.add_window( SettingsWindow(self) )
        self.add_window( ValidationSettingsWindow(self) )
        self.add_window( CameraSettingsWindow(self) )
    
    @property
    def windows(self):
        return self._windows
    
    def add_window(self, window: Window):
        self._windows[window.window_name] = window
    
    
    def render(self, camera_frame, scan_result: ScanResult):
        for window in self._windows.values():
            window.render(camera_frame, scan_result)
    


