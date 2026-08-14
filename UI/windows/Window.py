from abc import ABC, abstractmethod
import cv2

from UI.elements import Container
from utils.models import MouseData
from utils.Logger import logger


class Window(ABC):
    def __init__(self, window_name: str):
        self.window_name = window_name
        
        self._mouse = MouseData()
        self._root: Container = Container()
        
        self._enabled = False
        self._window_handle()

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
        logger.info(f"Opened {self.window_name}" if self._enabled else f"Closed {self.window_name}")

    @property
    def enabled(self):
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
    def render(self, frame=None):
        ...