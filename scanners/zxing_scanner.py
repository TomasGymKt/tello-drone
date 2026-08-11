import cv2
import zxingcpp
from utils.models import Corners, Int_Vector2, QR_Code
from utils.common import qr_size
from config import SCAN_ZXING_METHOD
from .base import Scanner as BaseScanner


def zxing_QR_scan(frame, scale: int=1) -> QR_Code | None:
    frame_height, frame_width = frame.shape[:2]

    screen_center_x: int = frame_width // 2
    screen_center_y: int = frame_height // 2

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
    points = Corners(
        Int_Vector2( int(result.position.top_left.x * scale)    , int(result.position.top_left.y * scale)     ),
        Int_Vector2( int(result.position.top_right.x * scale)   , int(result.position.top_right.y * scale)    ),
        Int_Vector2( int(result.position.bottom_right.x * scale), int(result.position.bottom_right.y * scale) ),
        Int_Vector2( int(result.position.bottom_left.x * scale) , int(result.position.bottom_left.y * scale)  )
    )

    # Get the center of the QR Code
    center_x = sum(x for x, _ in points) // 4
    center_y = sum(y for _, y in points) // 4


    size = qr_size(points) # Average length the sides in pixels

    # Get the pixel distance from the center of the frame
    error_x = center_x - screen_center_x
    error_y = center_y - screen_center_y
    
    
    qr_code = QR_Code(points, text, (center_x, center_y), size, (error_x, error_y))
    return qr_code


class Scanner(BaseScanner):
    method = SCAN_ZXING_METHOD

    def scan(self, frame) -> QR_Code | None:
        return zxing_QR_scan(frame)
