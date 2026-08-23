
import cv2

from UI.elements.Container import Container
from UI.elements.Shapes import Line, Circle, Outline
from UI.elements.Text import Text, TextStyle
from utils.models import Color, AlphaColor, QR_Code, ScanResult


class QRCodePloter(Container):
    def __init__(self):
        super().__init__()
        
        
        self._scan_result: ScanResult = ScanResult(success=False)
        self._outline = Outline(Color(0, 255, 0))
        self._line_center_qr = Line(0, 0, 0, 0, Color(255, 255, 0), 2)
        self._error_text = Text(0, 0, "dx:-- dy:--", TextStyle(Color(255, 255, 0), fontSize=0.5))
        self._center_circle = Circle(0, 0, 5, AlphaColor(0, 0, 255, 0.8))
        self._data_text = Text(0, 0, "-----")
        self._size_text = Text(0, 0, "Size: ---", TextStyle(Color(0, 255, 0), fontSize=0.5))
        self._distance_text = Text(0, 0, "Dist.: --- cm", TextStyle(Color(0, 255, 0), fontSize=0.5))
        
        self.add(self._outline)
        self.add(self._line_center_qr)
        self.add(self._center_circle)
        self.add(self._error_text)
        self.add(self._data_text)
        self.add(self._size_text)
        self.add(self._distance_text)
    
    def set_scan_result(self, scan_result: ScanResult):
        self._scan_result = scan_result
    
    def _handle_mouse(self, mouse):
        if self._scan_result is not None:
            return super()._handle_mouse(mouse)

    def _render(self, frame):
        if not self._scan_result.success:
            return
        
        frame_height, frame_width = frame.shape[:2]
        screen_center_x = int(frame_width / 2)
        screen_center_y = int(frame_height / 2)
        
        qr_code = self._scan_result.qr_code
        self._outline.set_points(qr_code.points)
        self._line_center_qr.set_position(screen_center_x, screen_center_y, qr_code.center_x, qr_code.center_y)
        self._center_circle.set_position(qr_code.center_x, qr_code.center_y)
        self._error_text_update(qr_code, screen_center_x, screen_center_y)
        self._data_text_update(qr_code)
        self._size_text_update(qr_code)
        self._distance_text_update(qr_code)
        return super()._render(frame)

    def _error_text_update(self, qr_code: QR_Code, screen_center_x: int, screen_center_y):
        text = f"dx:{qr_code.error_x} dy:{qr_code.error_y}"
    
        style = self._error_text._style
        (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, style.fontSize, style.fontThickness)
    
        text_x = (screen_center_x + qr_code.center_x) // 2 - text_width // 2
        text_y = (screen_center_y + qr_code.center_y) // 2 + text_height // 2
    
        self._error_text.set_text(text)
        self._error_text.set_position(text_x, text_y)
    
    def _data_text_update(self, qr_code: QR_Code):
        self._data_text.set_text(
            "No Data" if qr_code.text is None else qr_code.text,
            TextStyle(Color(0, 0, 255), fontSize=0.5) if qr_code.text is None else TextStyle(Color(0, 255, 0), fontSize=0.6)
        )
        self._data_text.set_position(qr_code.points.bottom_left.x, qr_code.points.bottom_left.y + 5)
    
    def _size_text_update(self, qr_code: QR_Code):
        self._size_text.set_text(
            f"Size: {qr_code.size:.0f}"
        )
        self._size_text.set_position(qr_code.points.top_left.x, qr_code.points.top_left.y - 49)
    
    def _distance_text_update(self, qr_code: QR_Code):
        self._distance_text.set_text(
            f"Dist.: {qr_code.distance_cm:.1f} cm"
        )
        self._distance_text.set_position(qr_code.points.top_left.x, qr_code.points.top_left.y - 25)
