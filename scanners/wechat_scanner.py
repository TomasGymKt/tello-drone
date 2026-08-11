import cv2
import numpy as np
import os
from utils.models import Corners, Int_Vector2, QR_Code
from utils.common import qr_size
from config import SCAN_WECHAT_METHOD
from .base import Scanner as BaseScanner


# Generated with AI


clahe = cv2.createCLAHE(
    clipLimit=2.5,
    tileGridSize=(8, 8)
)

models_dir = os.path.join(os.path.dirname(__file__), "wechat_models")


def _wechat_model_path(filename: str) -> str:
    path = os.path.join(models_dir, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Wechat QR model file not found: {path}")
    return path


we_detector = cv2.wechat_qrcode_WeChatQRCode(
    _wechat_model_path("detect.prototxt"),
    _wechat_model_path("detect.caffemodel"),
    _wechat_model_path("sr.prototxt"),
    _wechat_model_path("sr.caffemodel"),
)

def _try_detect(img, scale=1.0) -> QR_Code | None:
    texts, points = we_detector.detectAndDecode(img)

    if len(points) == 0:
        return None

    pts = (points[0] / scale).astype(int)

    corners = Corners(
        Int_Vector2(*pts[0]),
        Int_Vector2(*pts[1]),
        Int_Vector2(*pts[2]),
        Int_Vector2(*pts[3]),
    )

    center_x = int(pts[:, 0].mean())
    center_y = int(pts[:, 1].mean())

    size = qr_size(corners)

    h, w = img.shape[:2]

    return QR_Code(
        points=corners,
        text=texts[0] if len(texts) and texts[0] else None,
        center_xy=(center_x, center_y),
        size=size,
        error_xy=(
            center_x - int(w / scale) // 2,
            center_y - int(h / scale) // 2
        )
    )



def wechat_QR_scan(frame) -> QR_Code | None:

    # ---------- 1) originál ----------
    qr = _try_detect(frame)
    if qr:
        return qr

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # ---------- 2) CLAHE ----------
    enhanced = clahe.apply(gray)
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    qr = _try_detect(enhanced)
    if qr:
        return qr

    # ---------- 3) sharpen ----------
    kernel = [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ]

    kernel = np.array(kernel, dtype=np.float32)

    sharp = cv2.filter2D(enhanced, -1, kernel)

    qr = _try_detect(sharp)
    if qr:
        return qr

    # ---------- 4) 2x upscale ----------
    upscaled = cv2.resize(
        sharp,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_LANCZOS4
    )

    qr = _try_detect(upscaled, scale=2)
    if qr:
        return qr

    return None


class Scanner(BaseScanner):
    method = SCAN_WECHAT_METHOD

    def scan(self, frame) -> QR_Code | None:
        return wechat_QR_scan(frame)
