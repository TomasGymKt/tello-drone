import threading
import time

from utils.models import ScanResult
from settings import settings
from scanners import SCANNERS, scan_with



def scan_for_qr_code(frame, scan_method_order: list[str]) -> ScanResult:
    for scan_method in scan_method_order:
        qr_code = None

        if scan_method in SCANNERS:
            qr_code = scan_with(scan_method, frame)
        
        if qr_code is not None:
            return ScanResult(success=True,  qr_code=qr_code, scan_method=scan_method)
    
    return ScanResult(success=False)


class ScanWorker:
    def __init__(self, scan_method_order=settings.scan_method_order):
        self.scan_method_order = list(scan_method_order)

        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._latest_frame = None
        self._latest_result: ScanResult = ScanResult()
        self._is_running = True

        self._thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._thread.start()

    def submit_frame(self, frame) -> None:
        with self._condition:
            self._latest_frame = frame.copy()
            self._condition.notify()

    def get_latest_result(self) -> ScanResult:
        with self._lock:
            return self._latest_result

    def stop(self) -> None:
        with self._condition:
            self._is_running = False
            self._condition.notify_all()

        self._thread.join(timeout=1)

    def _worker_loop(self) -> None:
        while True:
            with self._condition:
                while self._is_running and self._latest_frame is None:
                    self._condition.wait()

                if not self._is_running:
                    return

                frame = self._latest_frame
                self._latest_frame = None

            scan_started_at = time.perf_counter()
            result = scan_for_qr_code(frame, self.scan_method_order)
            scan_finished_at = time.perf_counter()
            scan_ms = (scan_finished_at - scan_started_at) * 1000

            result.last_scan_ms = scan_ms
            result.last_scan_finished_at = scan_finished_at
            
            with self._lock:
                self._latest_result = result


