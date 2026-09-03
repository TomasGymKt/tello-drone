# djitellopy github: https://github.com/damiafuentes/DJITelloPy
# official docs: https://dl-cdn.ryzerobotics.com/downloads/tello/20180910/Tello%20SDK%20Documentation%20EN_1.3.pdf
# official docs (EDU?): https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf

from djitellopy import TelloException
import cv2
import time

from shared import tello, shared_qr

from utils.Logger import logger
from utils.errors import ConnectionError
from utils.common import PeriodicStatsLogger, check_wifi
from utils.color import C
from utils.DebugFrames import debug_frames
from utils.qr_validation import is_plausible_qr_code, longTermValidator
from UI.windows import window_controller
from settings import settings
from scanners.ScanWorker import ScanWorker
from fly import fly_worker


def main():

    check_wifi()

    try:
        tello.connect()
    except TelloException:
        raise ConnectionError("Failed to connect")
    logger.success(f"{C.BOLD}Connected to Tello{C.RESET}")
    periodic_stats = PeriodicStatsLogger()

    
    tello.streamon()
    
    frame_reader = tello.get_frame_read()

    scan_worker = ScanWorker()
    

    time.sleep(0.5)

    logger.info(f"{C.BOLD}Initialization complete{C.RESET}")
    try:
        # fly_worker.start()
        while True:
            frame = frame_reader.frame
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Color correction

            scan_worker.submit_frame(frame)
            result = scan_worker.get_latest_result()
            
            # Rejected non-square-ish QR Codes
            if result.success and not is_plausible_qr_code(result.qr_code):
                result.success = False
            
            if result.success:
                success = longTermValidator.validate(result.qr_code)
                result.success = success
                result.in_validation = not success
            longTermValidator.update()
            
            shared_qr.set(result.qr_code if result.success else None)
            
            window_controller.render(frame, result)
            
            # Draw windows from DebugFrames, useful in other threads since cv2 doesn't render windows in other threads
            for window_name, debug_frame in debug_frames.get_all().items():
                cv2.imshow(window_name, debug_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        periodic_stats.stop()
        fly_worker.stop()
        scan_worker.stop()
        cv2.destroyAllWindows()


def handle_program_exit():
    """Close windows and finalize the drone connection."""
    # TODO: Is this enough to PROPERLY stop?

    logger.info("Exiting program...")
    tello.send_rc_control(0, 0, 0, 0) # Stop moving
    tries = 4
    for i in range(tries): # If you spam Ctrl+C, it exits early
        try:
            tello.end() # and this doesn't finish
            break
        except KeyboardInterrupt:
            if i + 1 == tries:
                logger.warn("Exited without waiting for end() to finish.")
            else:
                logger.info(f"Don't spam Ctrl+C, the drone is {C.BOLD}already stoping{C.RESET}. Spam limit: {i+1}/{tries-1}")

    cv2.destroyAllWindows()
    logger.success(f"{C.BOLD}Successfuly exited program{C.RESET}")


if __name__ == "__main__":
    logger.success(f"{C.BOLD}Starting program...{C.RESET}")
    if settings.debug:
        logger.info(f"{C.YELLOW}Running in {C.BOLD}DEBUG MODE{C.RESET}{C.YELLOW}!{C.RESET}")
    if settings.is_emulator:
        logger.info(f"{C.YELLOW}Running on {C.BOLD}EMULATOR{C.RESET}{C.YELLOW}!{C.RESET}")

    try:
        main()

    except KeyboardInterrupt:
        logger.info(f"Keyboard interruped - {C.BRIGHT_RED}STOPPING{C.RESET}")
    
    except ConnectionError as err:
        logger.fatal(f"{C.BRIGHT_RED}Faild to connect{C.RESET} to Tello\n{err.msg}")
    
    except Exception as e:
        if settings.debug:
            raise e
        logger.error("Unknow error:", e)
    
    finally:
        handle_program_exit()
    
    
