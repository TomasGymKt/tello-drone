from dataclasses import dataclass, field
from typing import Final
from enum import StrEnum

TELLO_IP: Final = "192.168.10.1"
LOCALHOST_IP: Final = "127.0.0.1"

class ScanMethod(StrEnum):
    ZXING = "zxing"
    CV2 = "cv2"
    CONTOURS = "contours"
    WECHAT = "wechat"

@dataclass(slots=True)
class Settings:
    # ===== General =====

    debug: bool = True
    is_emulator: bool = True

    # ===== Scanning =====

    qr_code_size_cm: float = 10.0
    calibration_value: float = 9000.0

    scan_method_order: list[str] = field(default_factory=lambda: [
        ScanMethod.CV2,
    ])

    draw_ghost_qr_code: bool = True
    draw_rejected_qr_codes: bool = True
    qr_code_validation_preset: str = "balanced"

    @property
    def ip_address(self) -> str:
        if self.is_emulator:
            return LOCALHOST_IP
        return TELLO_IP
    
    @property
    def camera_focal_length(self) -> float:
        """Returns camera focal length in pixels"""
        return self.calibration_value / self.qr_code_size_cm
    

