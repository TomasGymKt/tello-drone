import math
import cv2
import numpy as np
from typing import TYPE_CHECKING

from UI.elements import Text, TextStyle, Slider, SliderStyle, Button, ButtonStyle, RadioGroup, Radio, RadioStyle, Container, Line
from UI.windows.Window import Window
from utils.common import is_window_open
from utils.models import AlphaColor, Color, QR_Code, ValidationPreset
from utils.Logger import logger
from settings import settings, shared

if TYPE_CHECKING:
    from UI.windows.WindowController import WindowController


class ValidationSettingsWindow(Window):
    def __init__(self, window_controller: WindowController, window_name="Validation Settings"):
        super().__init__(window_controller, window_name)
        self._base_frame = np.full((650, 685, 3), 255, dtype=np.uint8)
    
    def _setup(self):
        # === UI variables ===
        self._preset_name = settings.validation_preset
        self._all_presets = shared.get_validation_presets()

        
        # === UI elements ===
        self._preset_text = Text(188, 7, "Preset: -----", TextStyle(Color(255, 92, 255), AlphaColor(0, 0, 0, 0.8)))
        
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
        
        self._sliders_container = Container()
        self._sliders_container.enabled = self._preset_name == "custom"
        
        self._limit_min_side_slider            = Slider(420, 44 , 20.0 , 100.0, self._all_presets["custom"].min_side_px              , self._sliders_callback, SliderStyle(width=250))
        self._limit_max_side_slider            = Slider(420, 70 , 300.0, 650.0, self._all_presets["custom"].max_side_px              , self._sliders_callback, SliderStyle(width=250))
        self._limit_top_bottom_ratio_slider    = Slider(420, 96 , 0.5  , 3.0  , self._all_presets["custom"].max_top_bottom_side_ratio, self._sliders_callback, SliderStyle(width=250))
        self._limit_left_right_ratio_slider    = Slider(420, 122, 0.5  , 3.0  , self._all_presets["custom"].max_left_right_side_ratio, self._sliders_callback, SliderStyle(width=250))
        self._limit_adjacent_side_ratio_slider = Slider(420, 148, 0.5  , 3.0  , self._all_presets["custom"].max_adjacent_side_ratio  , self._sliders_callback, SliderStyle(width=250))
        self._limit_diagonal_ratio_slider      = Slider(420, 174, 0.5  , 3.0  , self._all_presets["custom"].max_diagonal_ratio       , self._sliders_callback, SliderStyle(width=250))
        self._limit_corner_dot_slider          = Slider(420, 239, 0.0  , 1.5  , self._all_presets["custom"].min_corner_dot           , self._sliders_callback, SliderStyle(width=250))
        
        self._picker_radio = RadioGroup(self._picker_radio_callback)
        self._picker_radio_setup()
        
        self._period_label_text = Text(7, 402, "Period:")
        self._period_slider = Slider(13, 436, 0, 5, settings.long_term_validation_settings.period, self._period_callback, SliderStyle(width=500))
        self._period_value_text = Text(525, 428, "--.--")
        self._appearance_label_text = Text(7, 465, "Minimum appearance:")
        self._appearance_slider = Slider(13, 499, 0, 10, settings.long_term_validation_settings.min_appearance, self._appearance_callback, SliderStyle(width=500))
        self._appearance_value_text = Text(525, 491, "-")
        self._gap_time_label_text = Text(7, 528, "Max gap time:")
        self._gap_time_slider = Slider(13, 562, 0, 10, settings.long_term_validation_settings.max_gap_time, self._gap_time_callback, SliderStyle(width=500))
        self._gap_time_value_text = Text(525, 554, "--")
        self._dist_mult_label_text = Text(7, 591, "Distance multiplier:")
        self._dist_mult_slider = Slider(13, 625, 0, 10, settings.long_term_validation_settings.dist_mult, self._dist_mult_callback, SliderStyle(width=500))
        self._dist_mult_value_text = Text(525, 617, "--")
        

        
        # === Add elements to root ===
        self._root.add(Text(7, 7, "Current values:", TextStyle(Color(255, 176, 0), AlphaColor(0, 0, 0, 0.8), fontSize=0.7, fontThickness=2)))
        self._root.add(self._preset_text)
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
        
        self._sliders_container.add(self._limit_min_side_slider)
        self._sliders_container.add(self._limit_max_side_slider)
        self._sliders_container.add(self._limit_top_bottom_ratio_slider)
        self._sliders_container.add(self._limit_left_right_ratio_slider)
        self._sliders_container.add(self._limit_adjacent_side_ratio_slider)
        self._sliders_container.add(self._limit_diagonal_ratio_slider)
        self._sliders_container.add(self._limit_corner_dot_slider)
        self._root.add(self._sliders_container)
        
        self._root.add(self._picker_radio)
        
        self._root.add(Line(7, 395, 678, 395, Color(200, 200, 200)))
        
        self._root.add(self._period_label_text)
        self._root.add(self._period_slider)
        self._root.add(self._period_value_text)
        self._root.add(self._appearance_label_text)
        self._root.add(self._appearance_slider)
        self._root.add(self._appearance_value_text)
        self._root.add(self._gap_time_label_text)
        self._root.add(self._gap_time_slider)
        self._root.add(self._gap_time_value_text)
        self._root.add(self._dist_mult_label_text)
        self._root.add(self._dist_mult_slider)
        self._root.add(self._dist_mult_value_text)
        
    
    def _render(self, camera_frame, scan_result):
        if not self._enabled:
            return
        
        if not is_window_open(self.window_name):
            self.set_enabled(False)
            return
        
        
        frame = self._base_frame.copy()
        
        self._preset_name = settings.validation_preset
        
        if scan_result.qr_code is not None:
            self._current_values_update(scan_result.qr_code)
        
        self._preset_text.set_text(f"Preset: {self._preset_name}")
        self._limit_texts_update()
        self._sliders_update()
        
        self._period_value_text.set_text(f"{settings.long_term_validation_settings.period:.2f}")
        self._appearance_value_text.set_text(f"{settings.long_term_validation_settings.min_appearance:.0f}")
        self._gap_time_value_text.set_text(f"{settings.long_term_validation_settings.max_gap_time:.2f}")
        self._dist_mult_value_text.set_text(f"{settings.long_term_validation_settings.dist_mult:.2f}")
        
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
        
        preset = self._all_presets[self._preset_name]
        
        self._min_side_text.set_text(
            f"Shortest side: {shortest_side:.3f} px",
            TextStyle(color=(Color(0, 255, 0) if shortest_side > preset.min_side_px else Color(0, 0, 255)))
        )
        self._max_side_text.set_text(
            f"Longest side: {longest_side:.3f} px",
            TextStyle(color=(Color(0, 255, 0) if longest_side < preset.max_side_px else Color(0, 0, 255)))
        )
        self._top_bottom_ratio_text.set_text(
            f"Top/Bottom ratio: {top_bottom_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if top_bottom_ratio < preset.max_top_bottom_side_ratio else Color(0, 0, 255)))
        )
        self._left_right_ratio_text.set_text(
            f"Left/Right ratio: {left_right_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if left_right_ratio < preset.max_left_right_side_ratio else Color(0, 0, 255)))
        )
        self._adjacent_side_ratio_text.set_text(
            f"Adjancet side ratio: {adjacent_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if adjacent_ratio < preset.max_adjacent_side_ratio else Color(0, 0, 255)))
        )
        self._diagonal_ratio_text.set_text(
            f"Diagonal ratio: {diagonal_ratio:.3f}",
            TextStyle(color=(Color(0, 255, 0) if diagonal_ratio < preset.max_diagonal_ratio else Color(0, 0, 255)))
        )
        for index, text in enumerate(self._corner_dot_texts):
            dot = dot_values[index]
            text.set_text(
                f"Corner dot {index}: {"None" if dot is None else f"{dot:.3f}"}",
                TextStyle(color=(Color(0, 255, 0) if dot is not None and dot < preset.min_corner_dot else Color(0, 0, 255)))
            )
    
    def _limit_texts_update(self):
        preset = self._all_presets[self._preset_name]
        
        self._limit_min_side_text.set_text(
            f"> {preset.min_side_px:.1f}"
        )
        self._limit_max_side_text.set_text(
            f"< {preset.max_side_px:.0f}"
        )
        self._limit_top_bottom_ratio_text.set_text(
            f"< {preset.max_top_bottom_side_ratio:.2f}"
        )
        self._limit_left_right_ratio_text.set_text(
            f"< {preset.max_left_right_side_ratio:.2f}"
        )
        self._limit_adjacent_side_ratio_text.set_text(
            f"< {preset.max_adjacent_side_ratio:.2f}"
        )
        self._limit_diagonal_ratio_text.set_text(
            f"< {preset.max_diagonal_ratio:.2f}"
        )
        self._limit_corner_dot_text.set_text(
            f"< {preset.min_corner_dot:.2f}"
        )
    
    def _sliders_update(self):
        enabled = self._preset_name == "custom"
        self._sliders_container.enabled = enabled
        
        for slider in self._sliders_container.elements:
            slider.set_style(
                SliderStyle(Color(255, 117, 0), handle_color=Color(255, 117, 0), width=250) 
                if enabled else 
                SliderStyle(Color(200, 200, 200), handle_color=Color(200, 200, 200), width=250)
            )
        
        preset = self._all_presets[self._preset_name]
        self._limit_min_side_slider.set_value(preset.min_side_px)
        self._limit_max_side_slider.set_value(preset.max_side_px)
        self._limit_top_bottom_ratio_slider.set_value(preset.max_top_bottom_side_ratio)
        self._limit_left_right_ratio_slider.set_value(preset.max_left_right_side_ratio)
        self._limit_adjacent_side_ratio_slider.set_value(preset.max_adjacent_side_ratio)
        self._limit_diagonal_ratio_slider.set_value(preset.max_diagonal_ratio)
        self._limit_corner_dot_slider.set_value(preset.min_corner_dot)
    
    def _sliders_callback(self, value: float):
        if self._preset_name != "custom":
            return
        new_preset = ValidationPreset(
            min_side_px=round(self._limit_min_side_slider.value, 1),
            max_side_px=round(self._limit_max_side_slider.value),
            max_top_bottom_side_ratio=round(self._limit_top_bottom_ratio_slider.value, 3),
            max_left_right_side_ratio=round(self._limit_left_right_ratio_slider.value, 3),
            max_adjacent_side_ratio=round(self._limit_adjacent_side_ratio_slider.value, 3),
            max_diagonal_ratio=round(self._limit_diagonal_ratio_slider.value, 3),
            min_corner_dot=round(self._limit_corner_dot_slider.value, 3),
        )
        shared.save_validation_preset("custom", new_preset)
        self._all_presets = shared.get_validation_presets()
    
    def _picker_radio_setup(self, start_x: int=7, start_y: int=330, end_x: int=685, gap: int=5):
        x = start_x
        y = start_y
        for preset_name in self._all_presets.keys():
            radio = Radio(0, 0, preset_name, preset_name)
            width = radio._text_width + radio._style.radius*2 + radio._style.circle_text_gap + radio._style.padding.horizontal + 1
            if x + width > end_x:
                x = start_x
                y += max(radio._style.radius * 2, radio._text_height) + radio._style.padding.vertical + 1 + gap
            radio.set_position(x, y)
            x += width + gap
            
            if preset_name == self._preset_name:
                self._picker_radio.select(radio)
            self._picker_radio.add(radio)
    
    def _picker_radio_callback(self, value: object):
        settings.validation_preset = value

    def _period_callback(self, value: float):
        settings.long_term_validation_settings.period = round(value, 2)
    
    def _appearance_callback(self, value: float):
        settings.long_term_validation_settings.min_appearance = round(value, 0)

    def _gap_time_callback(self, value: float):
        settings.long_term_validation_settings.max_gap_time = round(value, 2)

    def _dist_mult_callback(self, value: float):
        settings.long_term_validation_settings.dist_mult = round(value, 2)

