import cv2
import numpy as np
import os
from utils.models import QR_Code
from settings import ScanMethod
from .base import Scanner as BaseScanner


# Generated with AI


clahe = cv2.createCLAHE(
    clipLimit=2.5,
    tileGridSize=(8, 8)
)

models_dir = os.path.join(os.path.dirname(__file__), "wechat_models")


def _wechat_model_path(filename: str) -> str:
    """Resolve and validate a bundled WeChat QR model file.

    Args:
        filename: Model filename within the scanner's model directory.

    Returns:
        Existing absolute path to the requested model file.

    Raises:
        FileNotFoundError: If the requested model file is unavailable.
    """
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
    """Run the WeChat detector and map points back to source scale.

    Args:
        img: Image passed to the WeChat detector.
        scale: Resize scale applied before detection.

    Returns:
        Detected QR code, or None when no code is found.
    """
    texts, points = we_detector.detectAndDecode(img)

    if len(points) == 0:
        return None

    pts = (points[0] / scale).astype(int)

    
    return QR_Code(points=pts, text=texts[0] if len(texts) and texts[0] else None, frame=img)



def wechat_QR_scan(frame) -> QR_Code | None:
    """Scan a frame through several WeChat QR preprocessing passes.

    Args:
        frame: Image to scan.

    Returns:
        First detected QR code, or None when every pass fails.
    """

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
    """WeChat QR-code scanner backend with preprocessing fallbacks."""
    method = ScanMethod.WECHAT

    def scan(self, frame) -> QR_Code | None:
        """Scan an image with the WeChat QR detector.

        Args:
            frame: Image to scan.

        Returns:
            Detected QR code, or None when no code is found.
        """
        return wechat_QR_scan(frame)
