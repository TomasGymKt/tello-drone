import cv2

from UI.Elements import Container, Text, TextStyle
from UI.Pages.Page import Page
from utils.common import is_window_open
from utils.models import Color


class CameraPage(Page):
    def __init__(self):
        super().__init__("Tello")
        self._enabled = True
        self._window_handle()
    
    def render(self, frame):
        if not self._enabled:
            return
        
        if not is_window_open(self.window_name):
            self._window_handle()
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)


cameraPage = CameraPage()
ui = cameraPage.root

result_found_container: Container = ui.add(Container())
result_not_found_container: Container = ui.add(Container())
result_found_text: Text = result_found_container.add(Text(-7, 7, f"Method: ---", TextStyle(Color(0, 255, 0))))
result_not_found_container.add(Text(-7, 7, f"Not Found", TextStyle(Color(0, 0, 255))))


def set_found_result(found: bool, scan_method: str | None = None):
    if found:
        result_found_text.set_text(f"Method: {scan_method}")
    
    result_found_container.visible = found
    result_not_found_container.visible = not found
