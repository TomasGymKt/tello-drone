from abc import ABC, abstractmethod
import cv2
from typing import TYPE_CHECKING

from UI.elements import Container
from utils.models import MouseData, ScanResult
from utils.Logger import logger

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController
    

class Window(ABC):
    def __init__(self, window_controller: WindowController, window_name: str, enabled_by_default=False):
        self.window_name = window_name
        self._controller = window_controller
        
        self._mouse = MouseData()
        self._root: Container = Container()
        
        self._enabled = enabled_by_default
        self._window_handle()
        
        self._setup()
    
    @property
    def controller(self):
        return self._controller

    def _window_handle(self):
        if self._enabled:
            cv2.namedWindow(self.window_name)
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
        else:
            try:
                cv2.destroyWindow(self.window_name)
            except Exception:
                pass

    def set_enabled(self, enabled: bool):
        self._enabled = enabled
        self._window_handle()
        logger.debug(f"{"Opened" if self._enabled else "Closed"} window: {self.window_name}")

    @property
    def is_enabled(self):
        return self._enabled

    @property
    def root(self):
        return self._root
    
    def mouse_callback(self, event, x, y, flags, param):
        if not self._enabled:
            return
        
        self._mouse.event = event
        self._mouse.x = x
        self._mouse.y = y
        
        self._root.handle_mouse(self._mouse)
    
    
    @abstractmethod
    def render(self, camera_frame, scan_result: ScanResult):
        ...
    
    @abstractmethod
    def _setup(self):
        ...