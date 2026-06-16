from logger import logger
from errors import ConnectionError
from djitellopy import Tello, TelloException
import cv2
from utils import start_periodic_stats_log


def main(tello: Tello):

    try:
        tello.connect()
    except TelloException:
        raise ConnectionError
    logger.success("Connected to Tello")
    start_periodic_stats_log(tello)
    
    tello.streamon()
    
    frame_reader = tello.get_frame_read()

    while True:
        frame = frame_reader.frame

        cv2.imshow("Tello", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    
    cv2.destroyAllWindows()







def handle_program_exit(tello: Tello):
    # TODO: Is this enough to PROPERLY stop?

    logger.info("Exiting program...")
    tello.end()
    logger.success("Successfuly exited program")


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
        logger.error("Unknow error:", e)
    
    