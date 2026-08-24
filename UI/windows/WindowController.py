from UI.windows.CameraWindow import CameraWindow
from UI.windows.SettingsWindow import SettingsWindow
from UI.windows.ValidationSettingsWindow import ValidationSettingsWindow
from UI.windows.CameraSettingsWindow import CameraSettingsWindow
from UI.windows.FlyControlsWindow import FlyControllsWindow
from UI.windows.DroneWindows import DroneWindow
from UI.windows.Window import Window
from utils.models import ScanResult

class WindowController:
    """Own and render every application window."""

    def __init__(self):
        """Create and register the application's standard windows."""
        self._windows: dict[str, Window] = {}
        
        self.add_window( CameraWindow(self) )
        self.add_window( SettingsWindow(self) )
        self.add_window( ValidationSettingsWindow(self) )
        self.add_window( CameraSettingsWindow(self) )
        self.add_window( FlyControllsWindow(self) )
        self.add_window( DroneWindow(self) )
    
    @property
    def windows(self):
        """Return windows indexed by their configured names.

        Returns:
            Mapping from window names to window instances.
        """
        return self._windows
    
    def add_window(self, window: Window):
        """Register or replace a window by name.

        Args:
            window: Window instance to register.
        """
        self._windows[window.window_name] = window
    
    
    def render(self, camera_frame, scan_result: ScanResult):
        """Render each registered window.

        Args:
            camera_frame: Latest camera image available to windows.
            scan_result: Latest QR scan result available to windows.
        """
        for window in self._windows.values():
            window.render(camera_frame, scan_result)
    


