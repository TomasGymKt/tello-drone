import math
import threading
from dataclasses import dataclass
from typing import NamedTuple
from enum import StrEnum
from config import CAMERA_FOCAL_LENGTH_PX, QR_CODE_SIZE_CM, SCAN_ZXING_METHOD, SCAN_CV2_METHOD, SCAN_WECHAT_METHOD, SCAN_CONTOURS_METHOD

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


class SCAN_METHOD(StrEnum):
    ZXING = SCAN_ZXING_METHOD
    CV2 = SCAN_CV2_METHOD
    WECHAT = SCAN_WECHAT_METHOD
    CONTOURS = SCAN_CONTOURS_METHOD


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
        self.distance_cm = (QR_CODE_SIZE_CM * CAMERA_FOCAL_LENGTH_PX) / self.size
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


class ValidationPlausiblePresets(StrEnum):
    """
    Presets:
    - **verystrict**: old balanced behavior; square-ish only
    - **strict**: mild perspective/skew tolerance
    - **balanced**: allows noticeably skewed but still plausible quads
    - **loose**: for extreme viewing angles with higher false-positive risk
    - **veryloose**: maximum tolerance before shape checking becomes weak
    """
    
    VERY_STRICT = "verystrict"
    STRICT = "strict"
    BALANCED = "balanced"
    LOOSE = "loose"
    VERY_LOOSE = "veryloose"

@dataclass(slots=True)
class ValidationPlausiblePreset:
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
    
    # name: ValidationPlausiblePresets
    min_side_px: float
    max_side_px: float
    max_top_bottom_side_ratio: float
    max_left_right_side_ratio: float
    max_adjacent_side_ratio: float
    max_diagonal_ratio: float
    min_corner_dot: float
    
    def __repr__(self):
        min_side_px = self.min_side_px
        max_side_px = self.max_side_px
        max_top_bottom_side_ratio = self.max_top_bottom_side_ratio
        max_left_right_side_ratio = self.max_left_right_side_ratio
        max_diagonal_ratio = self.max_diagonal_ratio
        min_corner_dot = self.min_corner_dot
        return (
            "ValidationPlausiblePreset(\n"
            f"    {min_side_px=:.1f}\n"
            f"    {max_side_px=:.0f}\n"
            f"    {max_top_bottom_side_ratio=:.2f}\n"
            f"    {max_left_right_side_ratio=:.2f}\n"
            f"    {max_diagonal_ratio=:.2f}\n"
            f"    {min_corner_dot=:.2f}\n"
            ")"
        )