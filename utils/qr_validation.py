import math
from typing import Literal
from utils.common import timer
from utils.models import Color, QR_Code, ValidationPreset, ValidationPresets
from UI.elements.Text import Text, TextStyle

from utils.DebugFrames import debug_frames, create_blank_frame

PRESETS: dict[ValidationPresets, ValidationPreset] = {
    ValidationPresets.VERY_STRICT: ValidationPreset(
        min_side_px=40.0,
        max_side_px=500.0,
        max_top_bottom_side_ratio=1.30,
        max_left_right_side_ratio=1.30,
        max_adjacent_side_ratio=1.50,
        max_diagonal_ratio=1.30,
        min_corner_dot=0.35
    ),
    ValidationPresets.STRICT: ValidationPreset( # Restraints at the most extreme angles closer to the camera (from my simple testing)
        min_side_px=35.0,
        max_side_px=550.0,
        max_top_bottom_side_ratio=1.45,
        max_left_right_side_ratio=1.45,
        max_adjacent_side_ratio=1.75,
        max_diagonal_ratio=1.45,
        min_corner_dot=0.48
    ),
    ValidationPresets.BALANCED: ValidationPreset( # Works for every angle and distance cv2 can scan (from my simple testing)
        min_side_px=30.0,
        max_side_px=600.0,
        max_top_bottom_side_ratio=1.70,
        max_left_right_side_ratio=1.70,
        max_adjacent_side_ratio=2.10,
        max_diagonal_ratio=1.70,
        min_corner_dot=0.60
    ),
    ValidationPresets.LOOSE: ValidationPreset( # Unnecessarily loose, since balanced detectes everything cv2 can detect
        min_side_px=20.0,
        max_side_px=630.0,
        max_top_bottom_side_ratio=1.95,
        max_left_right_side_ratio=1.95,
        max_adjacent_side_ratio=2.50,
        max_diagonal_ratio=1.95,
        min_corner_dot=0.72
    ),
    ValidationPresets.VERY_LOOSE: ValidationPreset(
        min_side_px=20.0,
        max_side_px=630.0,
        max_top_bottom_side_ratio=2.25,
        max_left_right_side_ratio=2.25,
        max_adjacent_side_ratio=3.20,
        max_diagonal_ratio=2.25,
        min_corner_dot=0.82
    ),
    "custom": ValidationPreset(
        min_side_px=-1.0,
        max_side_px=-1.0,
        max_top_bottom_side_ratio=-1.0,
        max_left_right_side_ratio=-1.0,
        max_adjacent_side_ratio=-1.0,
        max_diagonal_ratio=-1.0,
        min_corner_dot=-1.0
    )
}


def is_plausible_qr_code(
    qr_code: QR_Code,
    preset: ValidationPresets,
) -> bool:
    """
    Extremely fast (<0.05 ms (on my hardware)) shape filter for rejecting detections that clearly do not look like a QR code.
    """
    
    preset_values = PRESETS[preset]
    min_side_px = preset_values.min_side_px
    max_side_px = preset_values.max_side_px
    max_opposite_side_ratio = preset_values.max_opposite_side_ratio
    max_adjacent_side_ratio = preset_values.max_adjacent_side_ratio
    max_diagonal_ratio = preset_values.max_diagonal_ratio
    min_corner_dot = preset_values.min_corner_dot


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
    shortest_side = min(side_lengths)
    longest_side = max(side_lengths)

    if shortest_side < min_side_px:
        return False
    
    if longest_side > max_side_px:
        return False

    if longest_side / shortest_side > max_adjacent_side_ratio:
        return False

    if max(top, bottom) / max(min(top, bottom), 1e-6) > max_opposite_side_ratio:
        return False

    if max(left, right) / max(min(left, right), 1e-6) > max_opposite_side_ratio:
        return False

    diagonal_a = math.dist(top_left, bottom_right)
    diagonal_b = math.dist(top_right, bottom_left)
    if max(diagonal_a, diagonal_b) / max(min(diagonal_a, diagonal_b), 1e-6) > max_diagonal_ratio:
        return False

    vectors = [
        (top_right.x - top_left.x, top_right.y - top_left.y),
        (bottom_right.x - top_right.x, bottom_right.y - top_right.y),
        (bottom_left.x - bottom_right.x, bottom_left.y - bottom_right.y),
        (top_left.x - bottom_left.x, top_left.y - bottom_left.y),
    ]

    for index in range(4):
        first = vectors[index]
        second = vectors[(index + 1) % 4]

        first_length = math.hypot(first[0], first[1])
        second_length = math.hypot(second[0], second[1])
        if first_length == 0 or second_length == 0:
            return False

        dot = abs(first[0] * second[0] + first[1] * second[1]) / (first_length * second_length)
        if dot > min_corner_dot:
            return False

    return True


def debug_is_plausible_qr_code(
    qr_code: QR_Code,
    preset: ValidationPresets,
) -> bool:
    """
    Extremely fast (<0.05 ms (on my hardware)) shape filter for rejecting detections that clearly do not look like a QR code.
    """
    
    preset_values = PRESETS[preset]
    min_side_px = preset_values.min_side_px
    max_side_px = preset_values.max_side_px
    max_top_bottom_side_ratio = preset_values.max_top_bottom_side_ratio
    max_left_right_side_ratio = preset_values.max_left_right_side_ratio
    max_adjacent_side_ratio = preset_values.max_adjacent_side_ratio
    max_diagonal_ratio = preset_values.max_diagonal_ratio
    min_corner_dot = preset_values.min_corner_dot


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
    
    fail_shortest_side = False
    fail_longest_side = False
    fail_adjacent_side_ratio = False
    fail_opposite_side_ratio_top_bottom = False
    fail_opposite_side_ratio_left_right = False
    fail_diagonal_ratio = False
    fail_corner_dot = False
    
    dot_values = [None, None, None, None]

    if shortest_side < min_side_px:
        fail_shortest_side = True
    
    if longest_side > max_side_px:
        fail_longest_side = True

    if longest_side / shortest_side > max_adjacent_side_ratio:
        fail_adjacent_side_ratio = True

    if max(top, bottom) / max(min(top, bottom), 1e-6) > max_top_bottom_side_ratio:
        fail_opposite_side_ratio_top_bottom = True

    if max(left, right) / max(min(left, right), 1e-6) > max_left_right_side_ratio:
        fail_opposite_side_ratio_left_right = True

    diagonal_a = math.dist(top_left, bottom_right)
    diagonal_b = math.dist(top_right, bottom_left)
    if max(diagonal_a, diagonal_b) / max(min(diagonal_a, diagonal_b), 1e-6) > max_diagonal_ratio:
        fail_diagonal_ratio = True

    vectors = [
        (top_right.x - top_left.x, top_right.y - top_left.y),
        (bottom_right.x - top_right.x, bottom_right.y - top_right.y),
        (bottom_left.x - bottom_right.x, bottom_left.y - bottom_right.y),
        (top_left.x - bottom_left.x, top_left.y - bottom_left.y),
    ]

    for index in range(4):
        first = vectors[index]
        second = vectors[(index + 1) % 4]

        first_length = math.hypot(first[0], first[1])
        second_length = math.hypot(second[0], second[1])
        if first_length == 0 or second_length == 0:
            fail_corner_dot = True
        else:
            dot = abs(first[0] * second[0] + first[1] * second[1]) / (first_length * second_length)
            dot_values[index] = dot
            if dot > min_corner_dot:
                fail_corner_dot = True
    
    
    debug = create_blank_frame(600, 600)
    Text(7, 7, f"Preset: {preset}").render(debug)
    Text(7, 35 , f"Shortest side: {shortest_side:.3f} > {min_side_px}"                                                                 , TextStyle(Color(0, 0, 255) if fail_shortest_side                  else (0, 255, 0))).render(debug)
    Text(7, 61 , f"Longest side: {longest_side:.3f} < {max_side_px}"                                                                   , TextStyle(Color(0, 0, 255) if fail_longest_side                   else (0, 255, 0))).render(debug)
    Text(7, 87 , f"Adjancet side ratio: {(longest_side / shortest_side):.3f} > {max_adjacent_side_ratio}"                              , TextStyle(Color(0, 0, 255) if fail_adjacent_side_ratio            else (0, 255, 0))).render(debug)
    Text(7, 113, f"Top/Bottom ratio: {(max(top, bottom) / max(min(top, bottom), 1e-6)):.3f} > {max_top_bottom_side_ratio}"             , TextStyle(Color(0, 0, 255) if fail_opposite_side_ratio_top_bottom else (0, 255, 0))).render(debug)
    Text(7, 139, f"Left/Right ratio: {(max(left, right) / max(min(left, right), 1e-6)):.3f} > {max_left_right_side_ratio}"             , TextStyle(Color(0, 0, 255) if fail_opposite_side_ratio_left_right else (0, 255, 0))).render(debug)
    Text(7, 165, f"Diagonal ratio: {(max(diagonal_a, diagonal_b) / max(min(diagonal_a, diagonal_b), 1e-6)):.3f} > {max_diagonal_ratio}", TextStyle(Color(0, 0, 255) if fail_diagonal_ratio                 else (0, 255, 0))).render(debug)
    for index in range(4):
        Text(
            7, 191 + (index*26),
            f"Corner dot {index}: {"None" if dot_values[index] is None else f"{dot_values[index]:.3f}"} > {min_corner_dot}",
            TextStyle(Color(0, 0, 255) if dot_values[index] is not None and dot_values[index] > min_corner_dot else (0, 255, 0))
        ).render(debug)

    debug_frames.set("QR Validation Debug", debug)

    if any([fail_shortest_side, fail_longest_side, fail_adjacent_side_ratio, fail_opposite_side_ratio_top_bottom, fail_opposite_side_ratio_left_right, fail_diagonal_ratio, fail_corner_dot]):
        return False

    return True

