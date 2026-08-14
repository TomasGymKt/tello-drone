from UI.windows.CameraWindow import CameraWindow
from UI.windows.SettingsWindow import SettingsWindow
from UI.windows.Window import Window

class WindowController:
    def __init__(self):
        self._windows: dict[str, Window] = {}
    
    def add_window(self, window: Window):
        self._windows[window.window_name] = window
    

windowController = WindowController()

# windowController.add_window( CameraWindow() )
# windowController.add_window( SettingsWindow() )