import math

from utils.models import QR_Code
from settings import settings, shared



def is_plausible_qr_code(qr_code: QR_Code) -> bool:
    """
    Extremely fast (<0.05 ms (on my hardware)) shape filter for rejecting detections that clearly do not look like a QR code.
    """
    
    preset = shared.get_validation_presets()[settings.validation_preset]
    
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

    if shortest_side < preset.min_side_px:
        return False
    
    if longest_side > preset.max_side_px:
        return False

    if longest_side / shortest_side > preset.max_adjacent_side_ratio:
        return False

    if max(top, bottom) / max(min(top, bottom), 1e-6) > preset.max_top_bottom_side_ratio:
        return False

    if max(left, right) / max(min(left, right), 1e-6) > preset.max_left_right_side_ratio:
        return False

    diagonal_a = math.dist(top_left, bottom_right)
    diagonal_b = math.dist(top_right, bottom_left)
    if max(diagonal_a, diagonal_b) / max(min(diagonal_a, diagonal_b), 1e-6) > preset.max_diagonal_ratio:
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
        if dot > preset.min_corner_dot:
            return False

    return True



