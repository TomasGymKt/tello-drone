from utils.logger import logger
from utils.models import QR_Code, Scan_Result
from config import DEFAULT_SCAN_METHOD_ORDER
from scanners import SCANNERS, scan_with




def scan_for_qr_code(frame, scan_method_order = DEFAULT_SCAN_METHOD_ORDER) -> Scan_Result | None:
    for scan_method in scan_method_order:
        qr_code = None

        if scan_method in SCANNERS:
            qr_code = scan_with(scan_method, frame)
        
        if qr_code is not None:
            return Scan_Result(qr_code, scan_method)
    
    return None