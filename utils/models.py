import threading
from dataclasses import dataclass
from typing import NamedTuple
from enum import StrEnum
from config import CAMERA_FOCAL_LENGTH_PX, QR_CODE_SIZE_CM, SCAN_ZXING_METHOD, SCAN_CV2_METHOD, SCAN_WECHAT_METHOD, SCAN_CONTOURS_METHOD


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
    def __init__(self, points: Corners, text: str | None, center_xy: tuple[int, int], size: float, error_xy: tuple[int, int]):
        self.points = points
        self.text = text
        self.center_xy = Int_Vector2(center_xy[0], center_xy[1])
        self.size = size
        self.distance_cm = (QR_CODE_SIZE_CM * CAMERA_FOCAL_LENGTH_PX) / size
        self.error_xy = Int_Vector2(error_xy[0], error_xy[1])

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


class Scan_Result(NamedTuple):
    qr_code: QR_Code
    scan_method: str

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