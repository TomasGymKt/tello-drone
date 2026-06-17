import threading
from djitellopy import Tello, BackgroundFrameRead
from utils import get_qr_code
from logger import logger

def move_to_qr_code(tello: Tello, error_x: int, error_y: int, distance_cm: float, SPEED: int=20):
    DEAD_ZONE_X = 40
    DEAD_ZONE_Y = 40
    DEAD_ZONE_DISTANCE = 15

    ERROR_Y_OFFSET = 30 # Because of the angle of the camera the drone flys higher then it shoudld

    error_y -= ERROR_Y_OFFSET

    left_right = 0
    forward_back = 0
    up_down = 0

    # Vlevo / vpravo
    if error_x > DEAD_ZONE_X:
        left_right = SPEED
    elif error_x < -DEAD_ZONE_X:
        left_right = -SPEED

    # Nahoru / dolů
    if error_y > DEAD_ZONE_Y:
        up_down = -SPEED
    elif error_y < -DEAD_ZONE_Y:
        up_down = SPEED

    # Vzdálenost od QR
    distance_error = distance_cm - 50

    if distance_error > DEAD_ZONE_DISTANCE:
        forward_back = SPEED
    elif distance_error < -DEAD_ZONE_DISTANCE:
        forward_back = -SPEED

    tello.send_rc_control(
    left_right,
    forward_back,
    up_down,
    0
    )



def main_loop(tello: Tello, frame_reader: BackgroundFrameRead):
    tello.takeoff()

    while True:
        frame = frame_reader.frame
        qr_code = get_qr_code(frame)

        if qr_code == None:
            tello.send_rc_control(0, 0, 0, 0)    # zastav
            continue

        points, text, (center_x, center_y), size, distance_cm, (error_x, error_y) = qr_code

        move_to_qr_code(tello, error_x, error_y, distance_cm)

        text = text.lower()

        if distance_cm < 60 and distance_cm > 40:
            if text == "vlevo":
                tello.rotate_counter_clockwise(90)
            elif text == "vpravo":
                tello.rotate_clockwise(90)
            elif text == "přistát":
                tello.land()
            else:
                logger.error("Unknow QR Code message")

        



def start_flying_thread(tello: Tello, frame_reader: BackgroundFrameRead):
    thread = threading.Thread(target=main_loop, args={tello: tello, frame_reader: frame_reader}, daemon=True)
    thread.start()