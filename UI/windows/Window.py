from abc import ABC, abstractmethod
import cv2
from typing import TYPE_CHECKING

from UI.elements import Container
from utils.common import is_window_open
from utils.models import MouseData, ScanResult
from utils.Logger import logger

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController
    

class Window(ABC):
    """Base OpenCV window with a root UI container and shared lifecycle."""

    def __init__(self, window_controller: WindowController, window_name: str, enabled_by_default=False):
        """Create and initialize a window.

        Args:
            window_controller: Controller that owns this window.
            window_name: OpenCV window title and controller lookup key.
            enabled_by_default: Whether to create the window immediately.
        """
        self.window_name = window_name
        self._controller = window_controller
        
        self._mouse = MouseData()
        self._root: Container = Container()
        
        self._enabled = enabled_by_default
        self._keep_enabled = False
        self._window_handle()
        
        self._setup()
    
    @property
    def controller(self):
        """Return the controller that owns this window.

        Returns:
            Window controller used to coordinate application windows.
        """
        return self._controller

    def _window_handle(self):
        """Create or destroy the native OpenCV window for the enabled state."""
        if self._enabled:
            cv2.namedWindow(self.window_name)
            cv2.setMouseCallback(self.window_name, self.mouse_callback)
        else:
            try:
                cv2.destroyWindow(self.window_name)
            except Exception:
                pass

    def set_enabled(self, enabled: bool):
        """Open or close the native window.

        Args:
            enabled: Whether the window should be open and rendered.
        """
        self._enabled = enabled
        self._window_handle()
        logger.debug(f"{"Opened" if self._enabled else "Closed"} window: {self.window_name}")

    @property
    def is_enabled(self):
        """Return whether the window is enabled.

        Returns:
            True when the window is currently enabled.
        """
        return self._enabled

    @property
    def root(self):
        """Return the root container for this window.

        Returns:
            Container that owns the window's UI elements.
        """
        return self._root
    
    def mouse_callback(self, event, x, y, flags, param):
        """Convert an OpenCV mouse callback into a root-container event.

        Args:
            event: OpenCV mouse event code.
            x: Pointer x-coordinate in pixels.
            y: Pointer y-coordinate in pixels.
            flags: OpenCV modifier-button flags.
            param: Optional OpenCV callback parameter.
        """
        if not self._enabled:
            return
        
        self._mouse.event = event
        self._mouse.x = x
        self._mouse.y = y
        
        self._root.handle_mouse(self._mouse)
    
    
    def render(self, camera_frame, scan_result: ScanResult):
        """Render the window when enabled and still open.

        Args:
            camera_frame: Latest camera image available to the window.
            scan_result: Latest QR scan result available to the window.
        """
        if not self._enabled:
            return
        
        if not is_window_open(self.window_name):
            if self._keep_enabled:
                self._window_handle()
                return
            self.set_enabled(False)
            return
        
        self._render(camera_frame, scan_result)
    
    @abstractmethod
    def _render(self, camera_frame, scan_result: ScanResult):
        """Implement window-specific rendering.

        Args:
            camera_frame: Latest camera image available to the window.
            scan_result: Latest QR scan result available to the window.
        """
        ...
    
    @abstractmethod
    def _setup(self):
        """Create this window's UI elements and persistent state."""
        ...
