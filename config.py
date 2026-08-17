DEFAULT_TELLO_IP = '192.168.10.1'
IP_ADDRES = DEFAULT_TELLO_IP # 127.0.0.1 for emulator / DEFAULT_TELLO_IP

IS_EMULATOR = True

if IS_EMULATOR:
  IP_ADDRES = "127.0.0.1"


IS_DEBUG = True

# ===== Scaning =====

QR_CODE_SIZE_CM = 10 # cm
CAMERA_FOCAL_LENGTH_PX = 9000 / QR_CODE_SIZE_CM # px   = (qr code size in px) * (physical distance in cm) / (physical qr code size in cm)


SCAN_ZXING_METHOD = "zxing"
SCAN_CV2_METHOD = "cv2"
SCAN_CONTOURS_METHOD = "contours"
SCAN_WECHAT_METHOD = "wechat"

# Order of QR code scaning methods
DEFAULT_SCAN_METHOD_ORDER = [
  # SCAN_ZXING_METHOD,
  SCAN_CV2_METHOD,
  # SCAN_WECHAT_METHOD,
  # SCAN_CONTOURS_METHOD
]
DRAW_GHOST_QR_CODE = True
DRAW_REJECTED_QR_CODES = True
QR_CODE_VALIDATION_DEFAULT_PLAUSIBLE_PRESET = "balanced"
# ===========


SHOULD_RIGHT_ALIGN_LOGS = False

# Specifications from official documention

MIN_OPERATING_TEMPERATURE = 0 # °C
MAX_OPERATING_TEMPERATURE = 40 # °C  bit weird because the drone reaches 60+°C regulary
