from draw import draw_cernter_cross, draw_info, draw_qrcodes
from utils.logger import logger
from utils.errors import ConnectionError
from djitellopy import Tello, TelloException
import cv2
from utils.common import FPSCounter, FrameTracker, start_periodic_stats_log, check_wifi, C
from utils.models import SharedQR
from scan import scan_for_qr_code
from fly import start_flying_thread
from config import IP_ADDRES, IS_DEBUG
import time



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
    
    fps_counter = FPSCounter()
    frame_tracker = FrameTracker()
    
    while True:
        frame = frame_reader.frame
        
        # Wait for a new frame (useful if we are processing at more than 30 FPS) - never gonna hapen
        if not IS_DEBUG and not frame_tracker.is_new_frame(frame):
            time.sleep(0.01)
            continue
        
        fps_counter.update()
        
        
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR) # Color correction
        canvas = frame.copy()

        result = scan_for_qr_code(frame, ["cv2"])
        
        if result:
            shared_qr.set(result.qr_code)
            draw_qrcodes(canvas, result.qr_code)
            draw_info(canvas, f"Method: {result.scan_method}", -7, 25, (0, 255, 0))
        else:
            shared_qr.set(None)
            draw_info(canvas, f"Not Found", -7, 25, (0, 0, 255))
            
        draw_cernter_cross(canvas)
        fps_counter.draw(canvas)


        cv2.imshow("Tello", canvas)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cv2.destroyAllWindows()




def handle_program_exit(tello: Tello):
    # TODO: Is this enough to PROPERLY stop?

    logger.info("Exiting program...")
    cv2.destroyAllWindows()
    tello.end()
    logger.success(f"{C.BOLD}Successfuly exited program{C.RESET}")


if __name__ == "__main__":
    logger.success(f"{C.BOLD}Starting program...{C.RESET}")

    tello = Tello(host=IP_ADDRES)

    try:
        main(tello)
        handle_program_exit(tello)

    except KeyboardInterrupt:
        logger.info(f"Keyboard interruped - {C.FG_BRIGHT_RED}STOPPING{C.RESET}")
    
    except ConnectionError as err:
        logger.fatal(f"{C.FG_BRIGHT_RED}Faild to connect{C.RESET} to Tello\n{err.msg}")
    
    except Exception as e:
        if IS_DEBUG: raise e
        logger.error("Unknow error:", e)
    
    finally:
        handle_program_exit(tello)
    
    