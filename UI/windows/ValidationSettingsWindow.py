

import math

import cv2
import numpy as np

from UI.elements import Text, TextStyle, Slider, SliderStyle, Button, ButtonStyle
from UI.windows.Window import Window
from utils.common import is_window_open
from utils.models import AlphaColor, Color, QR_Code, ValidationPreset
from utils.Logger import logger

from utils.qr_validation import PRESETS


class ValidationSettingsWindow(Window):
    def __init__(self, window_controller, window_name="Validation Settings"):
        super().__init__(window_controller, window_name, enabled_by_default=True)
        self._base_frame = np.full((500, 685, 3), 255, dtype=np.uint8)
    
    def _setup(self):
        # === UI variables ===

        
        # === UI elements ===
        self._min_side_text            = Text(7, 35 , "Shortest side: --- px")
        self._max_side_text            = Text(7, 61 , "Longest side: --- px")
        self._top_bottom_ratio_text    = Text(7, 87 , "Top/Bottom ratio: -.---")
        self._left_right_ratio_text    = Text(7, 113 , "Left/Right ratio: -.---")
        self._adjacent_side_ratio_text = Text(7, 139, "Adjancet side ratio: -.---")
        self._diagonal_ratio_text      = Text(7, 165, "Diagonal ratio: -.---")
        self._corner_dot_texts         = [
            Text(7, 191, "Corner dot 1: -.---"),
            Text(7, 217, "Corner dot 2: -.---"),
            Text(7, 243, "Corner dot 3: -.---"),
            Text(7, 269, "Corner dot 4: -.---")
        ]
        
        self._limit_min_side_text            = Text(320, 35 , "> --.-")
        self._limit_max_side_text            = Text(320, 61 , "< ---")
        self._limit_top_bottom_ratio_text    = Text(320, 87 , "> -.--")
        self._limit_left_right_ratio_text    = Text(320, 113, "> -.--")
        self._limit_adjacent_side_ratio_text = Text(320, 139, "> -.--")
        self._limit_diagonal_ratio_text      = Text(320, 165, "> -.--")
        self._limit_corner_dot_text          = Text(320, 230, "> -.--")
        
        self._limit_min_side_slider            = Slider(420, 44 , 20.0, 100.0, 50.0, lambda _: None, SliderStyle(width=250))
        self._limit_max_side_slider            = Slider(420, 70 , 300.0, 650.0, 500.0, lambda _: None, SliderStyle(width=250))
        self._limit_top_bottom_ratio_slider    = Slider(420, 96 , 0.5, 3.0, 1.5, lambda _: None, SliderStyle(width=250))
        self._limit_left_right_ratio_slider    = Slider(420, 122, 0.5, 3.0, 1.5, lambda _: None, SliderStyle(width=250))
        self._limit_adjacent_side_ratio_slider = Slider(420, 148, 0.5, 3.0, 1.5, lambda _: None, SliderStyle(width=250))
        self._limit_diagonal_ratio_slider      = Slider(420, 174, 0.5, 3.0, 1.5, lambda _: None, SliderStyle(width=250))
        self._limit_corner_dot_slider          = Slider(420, 239, 0.0, 1.5, 0.8, lambda _: None, SliderStyle(width=250))
        
        self._print_button = Button(7, 321, "Print set", self._print_button_callback)

        
        # === Add elements to root ===
        self._root.add(Text(7, 7, "Current values:", TextStyle(Color(255, 176, 0), AlphaColor(0, 0, 0, 0.8), fontSize=0.7, fontThickness=2)))
        self._root.add(self._min_side_text)
        self._root.add(self._max_side_text)
        self._root.add(self._top_bottom_ratio_text)
        self._root.add(self._left_right_ratio_text)
        self._root.add(self._adjacent_side_ratio_text)
        self._root.add(self._diagonal_ratio_text)
        for text in self._corner_dot_texts:
            self._root.add(text)
        
        self._root.add(self._limit_min_side_text)
        self._root.add(self._limit_max_side_text)
        self._root.add(self._limit_top_bottom_ratio_text)
        self._root.add(self._limit_left_right_ratio_text)
        self._root.add(self._limit_adjacent_side_ratio_text)
        self._root.add(self._limit_diagonal_ratio_text)
        self._root.add(self._limit_corner_dot_text)
        
        self._root.add(self._limit_min_side_slider)
        self._root.add(self._limit_max_side_slider)
        self._root.add(self._limit_top_bottom_ratio_slider)
        self._root.add(self._limit_left_right_ratio_slider)
        self._root.add(self._limit_adjacent_side_ratio_slider)
        self._root.add(self._limit_diagonal_ratio_slider)
        self._root.add(self._limit_corner_dot_slider)
        
        self._root.add(self._print_button)
        
    
    def render(self, camera_frame, scan_result):
        if not self._enabled:
            return
        
        if not is_window_open(self.window_name):
            self.set_enabled(False)
            return
        
        
        frame = self._base_frame.copy()
        
        if scan_result.qr_code is not None:
            self._current_values_update(scan_result.qr_code)
        
        self._limit_texts_uptade()
        
        self._root.render(frame)
        cv2.imshow(self.window_name, frame)
    
    def _current_values_update(self, qr_code: QR_Code):
        points = qr_code.points
        
        top_left = points.top_left
        top_right = points.top_right
        bottom_right = points.bottom_right
        bottom_left = points.bottom_left
    
        top = math.dist(top_left, top_right)
        right = math.dist(top_right, bottom_right)
        bottom = math.dist(bottom_right, bottom_left)
        left = math.dist(bottom_left, top_left)
    
        side_lengths = [top, right, bottom, left]
        shortest_side = max(min(side_lengths), 1e-6)
        longest_side = max(side_lengths)
        diagonal_tlbr = math.dist(top_left, bottom_right)
        diagonal_trbl = math.dist(top_right, bottom_left)
        
        top_bottom_ratio = max(top, bottom) / max(min(top, bottom), 1e-6)
        left_right_ratio = max(left, right) / max(min(left, right), 1e-6)
        adjacent_ratio = longest_side / shortest_side
        diagonal_ratio = max(diagonal_tlbr, diagonal_trbl) / max(min(diagonal_tlbr, diagonal_trbl), 1e-6)
        
        vectors = [
            (top_right.x - top_left.x, top_right.y - top_left.y),
            (bottom_right.x - top_right.x, bottom_right.y - top_right.y),
            (bottom_left.x - bottom_right.x, bottom_left.y - bottom_right.y),
            (top_left.x - bottom_left.x, top_left.y - bottom_left.y),
        ]
        
        dot_values = [None, None, None, None]
        
        for index in range(4):
            first = vectors[index]
            second = vectors[(index + 1) % 4]
    
            first_length = math.hypot(first[0], first[1])
            second_length = math.hypot(second[0], second[1])
            if first_length != 0 and second_length != 0:
                dot = abs(first[0] * second[0] + first[1] * second[1]) / (first_length * second_length)
                dot_values[index] = dot
        
        
        self._min_side_text.set_text(
            f"Shortest side: {shortest_side:.3f} px",
            TextStyle(color=(Color(0, 255, 0) if shortest_side > self._limit_min_side_slider.value else Color(0, 0, 255)))
        )
        self._max_side_text.set_text(
            f"Longest side: {longest_side:.3f} px",
            TextStyle(color=(Color(0, 255, 0) if longest_side < self._limit_max_side_slider.value else Color(0, 0, 255)))
        )
        self._top_bottom_ratio_text.set_text(
            f"Top/Bottom ratio: {top_bottom_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if top_bottom_ratio < self._limit_top_bottom_ratio_slider.value else Color(0, 0, 255)))
        )
        self._left_right_ratio_text.set_text(
            f"Left/Right ratio: {left_right_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if left_right_ratio < self._limit_left_right_ratio_slider.value else Color(0, 0, 255)))
        )
        self._adjacent_side_ratio_text.set_text(
            f"Adjancet side ratio: {adjacent_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if adjacent_ratio < self._limit_adjacent_side_ratio_slider.value else Color(0, 0, 255)))
        )
        self._diagonal_ratio_text.set_text(
            f"Diagonal ratio: {diagonal_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if diagonal_ratio < self._limit_diagonal_ratio_slider.value else Color(0, 0, 255)))
        )
        for index, text in enumerate(self._corner_dot_texts):
            dot = dot_values[index]
            text.set_text(
                f"Corner dot {index}: {"None" if dot is None else f"{dot:.3f}"}",
                TextStyle(color=(Color(0, 255, 0) if dot is not None and dot < self._limit_corner_dot_slider.value else Color(0, 0, 255)))
            )
    
    def _limit_texts_uptade(self):
        self._limit_min_side_text.set_text(
            f"> {self._limit_min_side_slider.value:.1f}"
        )
        self._limit_max_side_text.set_text(
            f"< {self._limit_max_side_slider.value:.0f}"
        )
        self._limit_top_bottom_ratio_text.set_text(
            f"< {self._limit_top_bottom_ratio_slider.value:.2f}"
        )
        self._limit_left_right_ratio_text.set_text(
            f"< {self._limit_left_right_ratio_slider.value:.2f}"
        )
        self._limit_adjacent_side_ratio_text.set_text(
            f"< {self._limit_adjacent_side_ratio_slider.value:.2f}"
        )
        self._limit_diagonal_ratio_text.set_text(
            f"< {self._limit_diagonal_ratio_slider.value:.2f}"
        )
        self._limit_corner_dot_text.set_text(
            f"< {self._limit_corner_dot_slider.value:.2f}"
        )
        
        # TODO: We need a settings manager to change stuff across files the right way
        # We don't have a way to make the validation code use the 'custom' preset
        # Nor can we get the current preset it's using
        PRESETS["custom"].min_side_px = self._limit_min_side_slider.value
        PRESETS["custom"].max_side_px = self._limit_max_side_slider.value
        PRESETS["custom"].max_top_bottom_side_ratio = self._limit_top_bottom_ratio_slider.value
        PRESETS["custom"].max_left_right_side_ratio = self._limit_left_right_ratio_slider.value
        PRESETS["custom"].max_adjacent_side_ratio = self._limit_adjacent_side_ratio_slider.value
        PRESETS["custom"].max_diagonal_ratio = self._limit_diagonal_ratio_slider.value
        PRESETS["custom"].min_corner_dot = self._limit_corner_dot_slider.value
    
    def _print_button_callback(self):
        # TODO: We need a settings manager to change stuff across files the right way
        # And to be able to permanetly store changes
        logger.info("Printing set:", PRESETS["custom"])
