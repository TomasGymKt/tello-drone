from djitellopy import Tello, TelloException
import cv2
import time

from config import DRAW_GHOST_QR_CODE, DRAW_REJECTED_QR_CODES, IP_ADDRES, IS_DEBUG, IS_EMULATOR
from utils.Logger import logger
from utils.errors import ConnectionError
from utils.common import start_periodic_stats_log, check_wifi, C
from utils.models import Color, MouseData, SharedQR
from utils.DebugFrames import debug_frames
from utils.PerformanceDisplay import PerformanceDisplay
from utils.qr_validation import debug_is_plausible_qr_code
from UI.Pages.CameraPage import cameraPage, set_found_result
from draw import draw_cernter_cross, draw_qrcodes
from scan import ScanWorker
from fly import start_flying_thread
from UI.Pages.SettingsPage import settings, create_settings_open_close_button



def main(tello: Tello):

    check_wifi()

    try:
        tello.connect()
    except TelloException:
        raise ConnectionError("Failed to connect")
    logger.success("Connected to Tello")
    start_periodic_stats_log(tello)

    
    tello.streamon()
    
    frame_reader = tello.get_frame_read()


    shared_qr = SharedQR()
    # start_flying_thread(tello, shared_qr)
    scan_worker = ScanWorker(["cv2"])
    
    performance_display = PerformanceDisplay()
    last_found_qr = None
    last_found_qr_time = None
    rejected_qr_code_points = None

    time.sleep(1)

    ui = cameraPage.root

    ui.add(performance_display.container)
    ui.add(create_settings_open_close_button(settings, -7, -7))

    try:
        while True:
            frame = frame_reader.frame
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Color correction

            scan_worker.submit_frame(frame)
            result, last_scan_ms, last_scan_finished_at = scan_worker.get_latest_result()
            
            # Rejected non-square-ish QR Codes
            if result is not None and not debug_is_plausible_qr_code(result.qr_code):
                rejected_qr_code_points = result.qr_code.points
                result = None
            
            if result is not None:
                shared_qr.set(result.qr_code)
            else:
                shared_qr.set(None)
            
            # Draw
            canvas = frame.copy()
            
            
            if DRAW_GHOST_QR_CODE and last_found_qr is not None:
                opacity = 0.4-(time.perf_counter()-last_found_qr_time)*1.5
                if opacity > 0:
                    draw_qrcodes(canvas, last_found_qr, opacity=opacity)

            if DRAW_REJECTED_QR_CODES and rejected_qr_code_points is not None:
                for i in range(4):
                    rejected_canvas = canvas.copy()
                    cv2.line(rejected_canvas, rejected_qr_code_points[i], rejected_qr_code_points[(i + 1) % 4], (0, 0, 255), 1)
                    cv2.addWeighted(rejected_canvas, 0.35, canvas, 0.65, 0, canvas)
                rejected_qr_code_points = None

            if result is not None:
                draw_qrcodes(canvas, result.qr_code)
                set_found_result(True, result.scan_method)
                last_found_qr = result.qr_code
                last_found_qr_time = time.perf_counter()
            else:
                set_found_result(False)
            
                
            draw_cernter_cross(canvas, ui)
            performance_display.update(last_scan_finished_at, last_scan_ms)
            
            
            
            cameraPage.render(canvas)
            settings.render()
            
            # Draw windows from DebugFrames, used in other threads since cv2 doesn't render windows in other threads
            for window_name, debug_frame in debug_frames.get_all().items():
                cv2.imshow(window_name, debug_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        scan_worker.stop()
        cv2.destroyAllWindows()


def handle_program_exit(tello: Tello):
    # TODO: Is this enough to PROPERLY stop?

    logger.info("Exiting program...")
    cv2.destroyAllWindows()
    tello.end()
    logger.success(f"{C.BOLD}Successfuly exited program{C.RESET}")


if __name__ == "__main__":
    logger.success(f"{C.BOLD}Starting program...{C.RESET}")
    if IS_DEBUG:
        logger.info(f"{C.FG_YELLOW}Running in {C.BOLD}DEBUG MODE{C.RESET}{C.FG_YELLOW}!{C.RESET}")
    if IS_EMULATOR:
        logger.info(f"{C.FG_YELLOW}Running on {C.BOLD}EMULATOR{C.RESET}{C.FG_YELLOW}!{C.RESET}")

    tello = Tello(host=IP_ADDRES)

    try:
        main(tello)
        handle_program_exit(tello)

    except KeyboardInterrupt:
        logger.info(f"Keyboard interruped - {C.FG_BRIGHT_RED}STOPPING{C.RESET}")
    
    except ConnectionError as err:
        logger.fatal(f"{C.FG_BRIGHT_RED}Faild to connect{C.RESET} to Tello\n{err.msg}")
    
    except Exception as e:
        if IS_DEBUG:
            raise e
        logger.error("Unknow error:", e)
    
    finally:
        handle_program_exit(tello)
    
    
