import cv2
from utils.errors import ScanningError
from utils.models import QR_Code
from utils.Logger import logger
from utils.color import C
from settings import ScanMethod
from .base import Scanner as BaseScanner


detector = cv2.QRCodeDetector()
def cv2_QR_scan(frame, try_decode=True) -> QR_Code | None:
    try:
        success, points = detector.detect(frame)
    except Exception as e:
        logger.error(f"cv2 QR code DETECTION threw an error{C.FG_RED}", e)
        print(C.RESET)
        raise ScanningError("cv2", e)

    if not success or points is None:
        return None
    
    
    text = None
    if try_decode:
        try:
            text, _ = detector.decode(frame, points)
        except Exception as e:
            logger.error(f"cv2 QR code DECODE threw an error{C.FG_RED}", e)
            print(C.RESET)
    if not text:
        text = None

    points = points.astype(int)[0]


    return QR_Code(points=points, text=text, frame=frame)


class Scanner(BaseScanner):
    method = ScanMethod.CV2

    def scan(self, frame) -> QR_Code | None:
        return cv2_QR_scan(frame, try_decode=True)
