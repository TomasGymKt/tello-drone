from config import CAMERA_FOCAL_LENGTH_PX, QR_CODE_SIZE_CM, SCAN_ZXING_METHOD, SCAN_CV2_METHOD, SCAN_WECHAT_METHOD, SCAN_CONTOURS_METHOD
import threading
from typing import NamedTuple
from enum import StrEnum


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
    