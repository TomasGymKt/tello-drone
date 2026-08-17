from djitellopy import Tello, TelloException
import cv2
import time

from config import IP_ADDRES, IS_DEBUG, IS_EMULATOR
from utils.Logger import logger
from utils.errors import ConnectionError
from utils.common import start_periodic_stats_log, check_wifi
from utils.color import C
from utils.models import SharedQR
from utils.DebugFrames import debug_frames
from utils.qr_validation import debug_is_plausible_qr_code, is_plausible_qr_code
from UI.windows.WindowController import WindowController
from ScanWorker import ScanWorker
from fly import start_flying_thread


def main(tello: Tello):

    check_wifi()

    try:
        tello.connect()
    except TelloException:
        raise ConnectionError("Failed to connect")
    logger.success(f"{C.BOLD}Connected to Tello{C.RESET}")
    start_periodic_stats_log(tello)

    
    tello.streamon()
    
    frame_reader = tello.get_frame_read()


    shared_qr = SharedQR()
    # start_flying_thread(tello, shared_qr)
    scan_worker = ScanWorker()
    

    time.sleep(1)
    
    windowController = WindowController()

    logger.info(f"{C.BOLD}Initialization complete{C.RESET}")
    try:
        while True:
            frame = frame_reader.frame
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Color correction

            scan_worker.submit_frame(frame)
            result = scan_worker.get_latest_result()
            
            # Rejected non-square-ish QR Codes
            if result.success and not debug_is_plausible_qr_code(result.qr_code):
                result.success = False
            
            if result.success:
                shared_qr.set(result.qr_code)
            else:
                shared_qr.set(None)
            
            windowController.render(frame, result)
            
            # Draw windows from DebugFrames, useful in other threads since cv2 doesn't render windows in other threads
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
    while True: # If you spam Ctrl+C, it exits early
        try:
            tello.end() # and this doesn't finish
            break
        except KeyboardInterrupt:
            logger.info(f"Don't spam Ctrl+C, it is {C.BOLD}already stoping{C.RESET} the drone")
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
    
    
