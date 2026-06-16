from logger import logger
from errors import ConnectionError
from djitellopy import Tello, TelloException
import time
from keyboard import is_pressed
import cv2
import turtle

def main(tello: Tello):

    try:
        tello.connect()
    except TelloException:
        raise ConnectionError
    logger.success("Connected to Tello")
    logger.info(f"Battery: {tello.get_battery()}%")
    
    tello.set_speed(40)
    tello.streamon()
    time.sleep(2)
    frame_read = tello.get_frame_read()
    #tello.set_video_resolution(Tello.RESOLUTION_480P)
    tello.set_video_fps(Tello.FPS_5)
    


    while not is_pressed('space'):
        pass
    # takeoff_and_landing(tello)
    while not is_pressed('esc'):
        img = frame_read.frame
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow("Tello Live Stream", img_rgb)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # while is_pressed('left'):
        #     tello.rotate_counter_clockwise(45)
        # while is_pressed('right'):
        #     tello.rotate_clockwise(45)
        # while is_pressed('up'):
        #     tello.move_forward(70)
        # while is_pressed('down'):
        #     tello.move_back(70)
        # while is_pressed('space'):
        #     tello.move_up(50)
        # while is_pressed('shift'):
        #     tello.move_down(50) 


def handle_program_exit(tello: Tello):
    # TODO: Is this enough to PROPERLY stop?

    
    logger.info("Exiting program...")
    tello.end()
    cv2.destroyAllWindows()
    logger.success("Successfuly exited program")






def takeoff_and_landing(tello: Tello):
    tello.takeoff()
    #time.sleep(10)
    # tello.land()
    #tello.end()


if __name__ == "__main__":
    logger.success("Starting program...")

    tello = Tello()

    try:
        main(tello)
        handle_program_exit(tello)

    except KeyboardInterrupt:
        logger.info("Keyboard interruped - \033[91mSTOPPING\033[0m")
        handle_program_exit(tello)
    
    except ConnectionError:
        logger.fatal("Faild to connect to Tello - \033[91mSTOPPING\033[0m")
    
    except Exception as e:
        logger.error("Unknown error:", e)
    