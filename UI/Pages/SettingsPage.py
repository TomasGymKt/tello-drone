import cv2
import numpy as np

from UI.Elements import Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Text, Slider, Container
from UI.Pages.Page import Page
from utils.Logger import logger
from utils.common import is_window_open
from utils.models import AlphaColor, Color

class SettingsPage(Page):
    def __init__(self):
        super().__init__("Settings")
        self._base_frame = np.full((600, 600, 3), 255, dtype=np.uint8)
    
    def render(self):
        if not self._enabled:
            return
        
        if not is_window_open(self.window_name):
            self.set_enabled(False)
            return
        
        frame = self._base_frame.copy()
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)


def create_settings_open_close_button(settingsPage: SettingsPage, x: int, y: int) -> Button:
    def callback():
        settingsPage.set_enabled(not settingsPage.enabled)
        
    return Button(
        x, y,
        "Close Settings" if settingsPage.enabled else "Open Settings",
        callback,
        ButtonStyle(background_color=(AlphaColor(84, 135, 25) if settingsPage.enabled else AlphaColor(69, 53, 220)))
    )



settings = SettingsPage()
root = settings.root

root.add(Button(7, 7, "Debug Render", lambda: root.set_debug_render(not root._show_debug_render), ButtonStyle(Color(0, 255, 0), AlphaColor(50, 50, 50))))
root.add(Button(-7, -7, "Button", lambda: print("press2!"), ButtonStyle(Color(0, 255, 0), AlphaColor(50, 50, 50))))

validatonContainer = Container()

def preset_callback(value: str):
    pass
    
validatonContainer.add(Text(7, 44, "Validation preset:"))
group = RadioGroup(preset_callback)
group.add(Radio(7, 70, "Very strict", "verystrict"))
group.add(Radio(7, 98, "Strict", "strict"))
group.add(Radio(7, 126, "Balanced", "balanced"))
group.add(Radio(7, 154, "Loose", "loose"))
group.add(Radio(7, 182, "Very loose", "veryloose"))

validatonContainer.add(group)

root.add(validatonContainer)

slider = Slider(250, 500, 0.0, 10.0, 5.0, lambda value: print(value))
root.add(slider)

