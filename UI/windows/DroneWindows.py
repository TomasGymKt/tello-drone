from __future__ import annotations
import cv2
from typing import TYPE_CHECKING

from shared import tello
from UI.elements import Text, TextStyle, Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Slider, SliderStyle, Container, Rectangle, Circle, Line
from UI.windows.Window import Window
from utils.common import create_blank_frame
from utils.models import AlphaColor, Color, Padding, ScanResult

from settings import settings

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController

class DroneWindow(Window):
    """Window for displaying state and changing drone parameters."""

    def __init__(self, window_controller: WindowController, window_name="Drone Settings"):
        """Create the drone settings window.

        Args:
            window_controller: Controller that owns this window.
            window_name: OpenCV title and controller lookup key.
        """
        super().__init__(window_controller, window_name, enabled_by_default=True)
        self._base_frame = create_blank_frame(400, 600)
    
    def _setup(self):
        """Create template elements."""
        # === UI variables ===
        
        
        # === UI elements ===
        self._pitch_text = Text(7, 7+0*26, "Pitch: -- deg")
        self._roll_text  = Text(7, 7+1*26, "Roll: -- deg" )
        self._yaw_text   = Text(7, 7+2*26, "Yaw: -- deg"  )
        self._speed_label  = Text(7, 7+3*26, "Speed")
        self._speed_x_text = Text(7+50, 7+4*26, "x: --")
        self._speed_y_text = Text(7+50, 7+5*26, "y: --")
        self._speed_z_text = Text(7+50, 7+6*26, "z: --")
        self._acceleration_label  = Text(7, 7+7*26, "Acceleration")
        self._acceleration_x_text = Text(7+50, 7+8*26, "x: --")
        self._acceleration_y_text = Text(7+50, 7+9*26, "y: --")
        self._acceleration_z_text = Text(7+50, 7+10*26, "z: --")
        self._distance_text = Text(7, 7+11*26, "TOF distance: -- cm")
        self._height_text = Text(7, 7+12*26, "Height: -- cm")
        self._barometer_text = Text(7, 7+13*26, "Barometer: ---.--")
        self._flight_time_text = Text(7, 7+14*26, "Flight time: -- s")
        self._battery_text = Text(7, 7+15*26, "Battery: -- %")
        self._temperature_text = Text(7, 7+16*26, "Temperature: -- C | -- C")

        self._optimal_height = Text(7, 7+17*26, "Optimal height: -- cm")
        
        
        # === Add elements to root ===
        self._root.add(self._pitch_text)
        self._root.add(self._roll_text)
        self._root.add(self._yaw_text)
        self._root.add(self._speed_label)
        self._root.add(self._speed_x_text)
        self._root.add(self._speed_y_text)
        self._root.add(self._speed_z_text)
        self._root.add(self._acceleration_label)
        self._root.add(self._acceleration_x_text)
        self._root.add(self._acceleration_y_text)
        self._root.add(self._acceleration_z_text)
        self._root.add(self._distance_text)
        self._root.add(self._height_text)
        self._root.add(self._barometer_text)
        self._root.add(self._flight_time_text)
        self._root.add(self._battery_text)
        self._root.add(self._temperature_text)

        self._root.add(self._optimal_height)
        
    
    def _render(self, camera_frame, scan_result: ScanResult):
        """Render the template elements.

        Args:
            camera_frame: Unused camera image supplied by the window lifecycle.
            scan_result: Unused QR result supplied by the window lifecycle.
        """
        frame = self._base_frame.copy()
        
        self._attitude_update()
        self._speed_update()
        self._acceleration_update()
        self._distance_text.set_text(f"TOF distance: {tello.get_distance_tof()} cm")
        self._height_text.set_text(f"Height: {tello.get_height()} cm")
        self._barometer_text.set_text(f"Barometer: {tello.get_barometer()}")
        self._flight_time_text.set_text(f"Flight time: {tello.get_flight_time()} s")
        self._battery_text.set_text(f"Battery: {tello.get_battery()} %")
        self._temperature_text.set_text(f"Temperature: {tello.get_lowest_temperature()} C | {tello.get_highest_temperature()} C")

        self._optimal_height.set_text(f"Optimal height: {settings.optimal_drone_height} cm")

        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    def _attitude_update(self):
        self._pitch_text.set_text(f"Pitch: {tello.get_pitch()} deg")
        self._roll_text.set_text(f"Roll: {tello.get_roll()} deg")
        self._yaw_text.set_text(f"Yaw: {tello.get_yaw()} deg")
    
    def _speed_update(self):
        self._speed_x_text.set_text(f"x: {tello.get_speed_x()}")
        self._speed_y_text.set_text(f"y: {tello.get_speed_y()}")
        self._speed_z_text.set_text(f"z: {tello.get_speed_z()}")
        
    def _acceleration_update(self):
        self._acceleration_x_text.set_text(f"x: {tello.get_acceleration_x()}")
        self._acceleration_y_text.set_text(f"y: {tello.get_acceleration_y()}")
        self._acceleration_z_text.set_text(f"z: {tello.get_acceleration_z()}")


