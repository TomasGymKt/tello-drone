import cv2
import numpy as np
import zxingcpp
from utils.models import Corners, Int_Vector2, QR_Code
from settings import ScanMethod
from .base import Scanner as BaseScanner


def zxing_QR_scan(frame, scale: int=1) -> QR_Code | None:
    """Scan a resized grayscale frame using ZXing.

    Args:
        frame: Image to scan.
        scale: Downscale factor trading readability for scan speed.

    Returns:
        First detected QR code, or None when no code is found.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Convert to grayscale
    small = cv2.resize(gray, None, fx=1 / scale, fy=1 / scale) # Set resolution scale, for faster scaning at the cost of readability (distance)
    
    results = zxingcpp.read_barcodes(small) # Get all the readable QR Codes

    # If none are found return None
    if len(results) == 0:
        return None
    
    # Use just one QR Code
    result = results[0] # TODO: What if there are more qr codes in frame
    
    text = str(result.text) # Get the data/text in the QR Code

    # The corners of the QR Code
    points = np.array([
        Int_Vector2( int(result.position.top_left.x * scale)    , int(result.position.top_left.y * scale)     ),
        Int_Vector2( int(result.position.top_right.x * scale)   , int(result.position.top_right.y * scale)    ),
        Int_Vector2( int(result.position.bottom_right.x * scale), int(result.position.bottom_right.y * scale) ),
        Int_Vector2( int(result.position.bottom_left.x * scale) , int(result.position.bottom_left.y * scale)  )
    ])
    

    return QR_Code(points=points, text=text, frame=frame)


class Scanner(BaseScanner):
    """ZXing QR-code scanner backend."""
    method = ScanMethod.ZXING

    def scan(self, frame) -> QR_Code | None:
        """Scan an image with ZXing.

        Args:
            frame: Image to scan.

        Returns:
            Detected QR code, or None when no code is found.
        """
        return zxing_QR_scan(frame)
