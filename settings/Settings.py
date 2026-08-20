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

@dataclass
class LongTermValidationSettings:
    period: float = 0.2 # Minimum time before a QR code can be valid
    # keep in mind that a QR code has to be scaned min_appearance times in the period, so for an example:
    #   period=0.2, min_appearance=2
    #   = 1 scaned QR code per 100 ms => scanner has to be running at 10 FPS or more
    max_gap_time: float = 2 # Maximum time a zone stays active after it's QR code disappears
    min_appearance: int = 2 # Minimum amount of times a QR code has to appear in the same zone, for it to be valid
    dist_mult: float = 0.5 # Radius multiplier of the zone; 1.0 = half QR code size

@dataclass(slots=True)
class Settings:
    # ===== General =====

    debug: bool = True
    is_emulator: bool = False

    # ===== Scanning =====

    qr_code_size_cm: float = 10.0
    camera_focal_length: float = 900.0 # = (qr code size in px) * (physical distance in cm) / (physical qr code size in cm)

    scan_method_order: list[str] = field(default_factory=lambda: [
        ScanMethod.CV2,
    ])

    draw_ghost_qr_code: bool = True
    draw_rejected_qr_codes: bool = True
    validation_preset: str = "balanced"
    long_term_validation_settings: LongTermValidationSettings = field(default_factory=lambda: LongTermValidationSettings())

    @property
    def ip_address(self) -> str:
        if self.is_emulator:
            return LOCALHOST_IP
        return TELLO_IP
    
    @property
    def calibration_value(self) -> float:
        return self.camera_focal_length * self.qr_code_size_cm
    

