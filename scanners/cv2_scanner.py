import cv2
from utils.models import Corners, Int_Vector2, QR_Code
from utils.common import qr_size
from utils.Logger import logger
from utils.errors import ScanningError
from config import SCAN_CV2_METHOD
from .base import Scanner as BaseScanner


detector = cv2.QRCodeDetector()
def cv2_QR_scan(frame, try_decode=True) -> QR_Code | None:
    try:
        success, points = detector.detect(frame)
    except Exception as e:
        logger.error("cv2 QR code DETECTION threw an error", e)
        raise ScanningError("cv2", e)

    if not success or points is None:
        return None
    
    
    text = None
    if try_decode:
        try:
            text, _ = detector.decode(frame, points)
        except Exception as e:
            logger.error("cv2 QR code DECODE threw an error", e)
            raise ScanningError("cv2", e)
    if not text:
        text = None

    points = points.astype(int)[0]

    corners = Corners(
        top_left=Int_Vector2(*points[0]),
        top_right=Int_Vector2(*points[1]),
        bottom_right=Int_Vector2(*points[2]),
        bottom_left=Int_Vector2(*points[3]),
    )
    

    center_x = int(points[:, 0].mean())
    center_y = int(points[:, 1].mean())

    size = qr_size(corners)

    frame_h, frame_w = frame.shape[:2]
    error_x = center_x - frame_w // 2
    error_y = center_y - frame_h // 2

    return QR_Code(points=corners, text=text, center_xy=(center_x, center_y), size=size, error_xy=(error_x, error_y))


class Scanner(BaseScanner):
    method = SCAN_CV2_METHOD

    def scan(self, frame) -> QR_Code | None:
        return cv2_QR_scan(frame, try_decode=True)
