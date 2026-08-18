import math
import threading
from dataclasses import asdict, dataclass
from typing import NamedTuple
from enum import StrEnum
from settings import settings

def qr_size(points: Corners) -> float:
    top = math.dist(points.top_left, points.top_right)
    right = math.dist(points.top_right, points.bottom_right)
    bottom = math.dist(points.bottom_right, points.bottom_left)
    left = math.dist(points.bottom_left, points.top_left)

    return (top + right + bottom + left) / 4

class Int_Vector2(NamedTuple):
    x: int
    y: int


class Corners(NamedTuple):
    top_left: Int_Vector2
    top_right: Int_Vector2
    bottom_right: Int_Vector2
    bottom_left: Int_Vector2


class QR_Code:
    def __init__(self, points, text: str | None, frame):
        self.points = Corners(
            top_left=Int_Vector2(*points[0]),
            top_right=Int_Vector2(*points[1]),
            bottom_right=Int_Vector2(*points[2]),
            bottom_left=Int_Vector2(*points[3]),
        )
        self.text = text
        self.center_x = int(points[:, 0].mean())
        self.center_y = int(points[:, 1].mean())
        self.size = qr_size(self.points)
        self.distance_cm = settings.calibration_value / self.size
        self.error_x = self.center_x - frame.shape[1] // 2
        self.error_y = self.center_y - frame.shape[0] // 2

class SharedQR:
    def __init__(self):
        self.lock = threading.Lock()
        self.qr_code: QR_Code | None = None

    def set(self, qr_code: QR_Code | None):
        with self.lock:
            self.qr_code = qr_code

    def get(self):
        with self.lock:
            return self.qr_code


@dataclass(slots=True)
class ScanResult():
    success: bool = False
    qr_code: QR_Code | None = None
    scan_method: str | None = None
    last_scan_ms: float | None = None
    last_scan_finished_at: float | None = None

class Padding:
    def __init__(self, top: int = 0, right: int | None = None, bottom: int | None = None, left: int | None = None):
        if right is None:
            right = top

        if bottom is None:
            bottom = top

        if left is None:
            left = right

        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        
    @property
    def horizontal(self):
        return self.left + self.right

    @property
    def vertical(self):
        return self.top + self.bottom


class Color(tuple):
    def __new__(cls, *args):
        if len(args) == 1:
            color = args[0]

            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("Color requires a (b, g, r) tuple")

            b, g, r = color

        elif len(args) == 3:
            b, g, r = args

        else:
            raise ValueError("Color requires (b, g, r) or b, g, r")

        return super().__new__(cls, (b, g, r))


class AlphaColor(Color):
    def __new__(cls, *args):
        if len(args) == 1:
            color = args[0]
            alpha = 1.0

            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("AlphaColor requires a (b, g, r) tuple")

            b, g, r = color

        elif len(args) == 2:
            color, alpha = args

            if not isinstance(color, tuple) or len(color) != 3:
                raise ValueError("AlphaColor requires a (b, g, r) tuple")

            b, g, r = color

        elif len(args) == 3:
            b, g, r = args
            alpha = 1.0

        elif len(args) == 4:
            b, g, r, alpha = args

        else:
            raise ValueError(
                "AlphaColor requires (b, g, r), b, g, r, ((b, g, r), alpha) or b, g, r, alpha"
            )

        return super().__new__(cls, b, g, r)

    def __init__(self, *args):
        if len(args) == 1 or len(args) == 3:
            self.alpha = 1.0
        elif len(args) == 2:
            self.alpha = args[1]
        else:
            self.alpha = args[3]


@dataclass(slots=True)
class MouseData:
    x: int = -1
    y: int = -1
    event: int = -1


@dataclass(slots=True)
class ValidationPreset:
    """
    Parameter meaning:
    - **min_side_px**: shortest side must be at least this long; higher is stricter
    - **min_side_px**: longest side must be at most this long; lower is stricter
    - **max_top_bottom_side_ratio**: top vs bottom side mismatch; 1.0 means equal
    - **max_left_right_side_ratio**: left vs right side mismatch; 1.0 means equal
    - **max_adjacent_side_ratio**: longest side / shortest side; limits overall stretching
    - **max_diagonal_ratio**: mismatch between the two diagonals; lower is squarer
    - **min_corner_dot**: corner right-angle tolerance using normalized dot product; lower is stricter
    """
    
    min_side_px: float
    max_side_px: float
    max_top_bottom_side_ratio: float
    max_left_right_side_ratio: float
    max_adjacent_side_ratio: float
    max_diagonal_ratio: float
    min_corner_dot: float
    
    def to_dict(self) -> dict:
        return asdict(self)

    