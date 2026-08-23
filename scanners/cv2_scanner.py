import cv2
from utils.errors import ScanningError
from utils.models import QR_Code
from utils.Logger import logger
from utils.color import C
from settings import ScanMethod
from .base import Scanner as BaseScanner


detector = cv2.QRCodeDetector()
def cv2_QR_scan(frame, try_decode=True) -> QR_Code | None:
    """Detect and optionally decode a QR code using OpenCV.

    Args:
        frame: Image to scan.
        try_decode: Whether to decode payload text after detection.

    Returns:
        Detected QR code, or None when no code is found.

    Raises:
        ScanningError: If OpenCV detection raises an exception.
    """
    try:
        success, points = detector.detect(frame)
    except Exception as e:
        logger.error(f"cv2 QR code DETECTION threw an error{C.RED}", e)
        print(C.RESET)
        raise ScanningError("cv2", e)

    if not success or points is None:
        return None
    
    
    text = None
    if try_decode:
        try:
            text, _ = detector.decode(frame, points)
        except Exception as e:
            logger.error(f"cv2 QR code DECODE threw an error{C.RED}", e)
            print(C.RESET)
    if not text:
        text = None

    points = points.astype(int)[0]


    return QR_Code(points=points, text=text, frame=frame)


class Scanner(BaseScanner):
    """OpenCV QR-code scanner backend."""
    method = ScanMethod.CV2

    def scan(self, frame) -> QR_Code | None:
        """Scan an image with OpenCV's QR detector.

        Args:
            frame: Image to scan.

        Returns:
            Detected QR code, or None when no code is found.
        """
        return cv2_QR_scan(frame, try_decode=True)
