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
    camera_focal_length: float = 900.0 # = (qr code size in px) * (physical distance in cm) / (physical qr code size in cm)

    scan_method_order: list[str] = field(default_factory=lambda: [
        ScanMethod.CV2,
    ])

    draw_ghost_qr_code: bool = True
    draw_rejected_qr_codes: bool = True
    validation_preset: str = "balanced"

    @property
    def ip_address(self) -> str:
        if self.is_emulator:
            return LOCALHOST_IP
        return TELLO_IP
    
    @property
    def calibration_value(self) -> float:
        return self.camera_focal_length * self.qr_code_size_cm
    

