import time

import cv2
import numpy as np
from typing import TYPE_CHECKING
from shared import tello

from UI.elements import Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Text, Slider, Container, Rectangle
from UI.windows.Window import Window
from utils.Logger import logger
from utils.common import create_blank_frame
from utils.models import AlphaColor, Color, ScanResult, Padding

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class FlyControllsWindow(Window):
    """Menu window for controlling the drone."""

    def __init__(self, window_controller: WindowController, window_name="Fly Controls"):
        """Create the fly controls window.

        Args:
            window_controller: Controller that owns this window.
            window_name: OpenCV title and controller lookup key.
        """
        super().__init__(window_controller, window_name)
        self._base_frame = create_blank_frame(323, 205)
    
    def _setup(self):
        """Create control buttons"""
        # === UI variables ===
        self._waiting_for_emergency = True
        self._is_emergency = False
        self._start_emergency = 0
        self._start_hold_time = 0
        self._emergency_holding_time = 1.2
        
        self._keep_alive_time = 0
        self._keep_alive_limit = 13
        
        
        # === UI elements ===
        self._window_overlay = Rectangle(0, 0, 323, 205, AlphaColor(0, 0, 255, 0.1))
        self._window_overlay.visible = False
        self._fly_buttons_container = Container()
        self._forward_button     = Button(81 , 10, "/\\", self._forward_callback    , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=0.8, fontThickness=5, padding=Padding(25, 15)))
        self._backward_button    = Button(81 , 81, "\\/", self._backward_callback   , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=0.8, fontThickness=5, padding=Padding(25, 15)))
        self._left_button        = Button(10 , 81, "<"  , self._left_callback       , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=1  , fontThickness=5, padding=Padding(23, 21, 23, 20)))
        self._right_button       = Button(152, 81, ">"  , self._right_callback      , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=1  , fontThickness=5, padding=Padding(23, 21, 23, 20)))
        self._clockwise_button   = Button(152, 10, "^O" , self._clockwise_callback  , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=1.2, fontThickness=4, padding=Padding(22, 7, 21, 6)))
        self._counterwise_button = Button(10 , 10, "O^" , self._counterwise_callback, ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=1.2, fontThickness=4, padding=Padding(22, 7, 21, 6)))
        self._up_button          = Button(243, 10, "/\\", self._up_callback         , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=0.8, fontThickness=5, padding=Padding(25, 15)))
        self._down_button        = Button(243, 81, "\\/", self._down_callback       , ButtonStyle(background_color=AlphaColor(60, 60, 60), pressed_background_color=AlphaColor(30, 30, 30), fontSize=0.8, fontThickness=5, padding=Padding(25, 15)))
        self._control_button = Button(10, 170, "Take off/Land", self._control_callback, ButtonStyle(padding=Padding(5, 38)))
        self._emergency_button = Button(243, 170, "eStop", self._emergency_callback, ButtonStyle(background_color=AlphaColor(50, 50, 200), padding=Padding(5, 8)))
        self._emergency_button_overlay = Rectangle(243, 170, 243, 195, AlphaColor(50, 50, 0, 0.2))
        self._emergency_button_overlay.visible = False
        
        
        # === Add elements to root ===
        self._root.add(self._window_overlay)
        self._fly_buttons_container.add(self._forward_button)
        self._fly_buttons_container.add(self._backward_button)
        self._fly_buttons_container.add(self._left_button)
        self._fly_buttons_container.add(self._right_button)
        self._fly_buttons_container.add(self._clockwise_button)
        self._fly_buttons_container.add(self._counterwise_button)
        self._fly_buttons_container.add(self._up_button)
        self._fly_buttons_container.add(self._down_button)
        self._root.add(self._fly_buttons_container)
        self._root.add(self._control_button)
        self._root.add(self._emergency_button)
        self._root.add(self._emergency_button_overlay)
        
    
    def _render(self, camera_frame, scan_result: ScanResult):
        """Render the controls.

        Args:
            camera_frame: Unused camera image supplied by the window lifecycle.
            scan_result: Unused QR result supplied by the window lifecycle.
        """
        frame = self._base_frame.copy()

        self._fly_buttons_container.enabled = tello.is_flying
        self._fly_buttons_container.opacity = 1.0 if tello.is_flying else 0.2
        self._control_update()
        self._emergency_update()
        
        if time.perf_counter() - self._keep_alive_time >= self._keep_alive_limit:
            self._keep_alive_time = time.perf_counter()
            # tello.send_control_command("command")
            tello.send_rc_control(0, 0, 0, 0)
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    
    def _forward_callback(self):
        if not tello.is_flying:
            return
        tello.move_forward(50)
    
    def _backward_callback(self):
        if not tello.is_flying:
            return
        tello.move_back(50)
    
    def _left_callback(self):
        if not tello.is_flying:
            return
        tello.move_left(50)
    
    def _right_callback(self):
        if not tello.is_flying:
            return
        tello.move_right(50)
    
    def _up_callback(self):
        if not tello.is_flying:
            return
        tello.move_up(50)
        
    def _down_callback(self):
        if not tello.is_flying:
            return
        tello.move_down(50)
    
    def _clockwise_callback(self):
        if not tello.is_flying:
            return
        tello.rotate_clockwise(45)
        
    def _counterwise_callback(self):
        if not tello.is_flying:
            return
        tello.rotate_counter_clockwise(45)
    
    def _control_callback(self):
        if tello.is_flying:
            tello.land()
        else:
            tello.takeoff()

    def _control_update(self):
        if tello.is_flying:
            self._control_button.set_text("Land", ButtonStyle(background_color=AlphaColor(0, 0, 150), padding=Padding(5, 84, 5, 83)))
        else:
            self._control_button.set_text("Take off", ButtonStyle(background_color=AlphaColor(0, 80, 0), padding=Padding(5, 67)))
    
    def _emergency_callback(self):
        if not self._waiting_for_emergency:
            self._emergency_button.set_text("eStop", ButtonStyle(background_color=AlphaColor(50, 50, 200), padding=Padding(5, 8)))
            self._waiting_for_emergency = True
            return
        
        if not self._is_emergency:
            self._start_emergency = time.perf_counter()
            self._is_emergency = True
            self._emergency_button.set_text("HOLD", ButtonStyle(background_color=AlphaColor(50, 50, 200), pressed_background_color=AlphaColor(50, 50, 255), padding=Padding(5, 10)))
            self._window_overlay.visible = True
            return
        
        self._emergency_button_overlay.visible = False
        self._start_hold_time = 0
    
    def _emergency_update(self):
        now = time.perf_counter()
        if self._is_emergency:
            if self._start_hold_time == 0:
                if now - self._start_emergency >= 3:
                    self._start_emergency = 0
                    self._is_emergency = False
                    self._emergency_button.set_text("eStop", ButtonStyle(background_color=AlphaColor(50, 50, 200), padding=Padding(5, 8)))
                    self._window_overlay.visible = False
                
                if self._emergency_button.is_pressed:
                    self._emergency_button_overlay.visible = True
                    self._start_hold_time = now
                
            else:
                if now - self._start_hold_time >= self._emergency_holding_time:
                    self._emergency()
                    self._is_emergency = False
                    self._start_emergency = 0
                    self._start_hold_time = 0
                    self._emergency_button.set_text("eStop", ButtonStyle(background_color=AlphaColor(200, 200, 50), padding=Padding(5, 8)))
                    self._emergency_button_overlay.visible = False
                    self._window_overlay.visible = False
                    self._waiting_for_emergency = False
                    
                self._start_emergency = now
                percent = (now - self._start_hold_time) / self._emergency_holding_time
                x2 = int(243 + 70 * percent)
                self._emergency_button_overlay.set_position(243, 170, x2, 194)
                
        if not self._emergency_button.is_hovered:
            self._start_hold_time = 0
    
    def _emergency(self):
        tello.emergency()

