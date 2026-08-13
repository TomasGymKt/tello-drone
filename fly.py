import threading
from djitellopy import Tello, BackgroundFrameRead
from utils.models import SharedQR
from utils.Logger import logger

def move_to_qr_code(tello: Tello, error_x: int, error_y: int, distance_cm: float, SPEED: int=20):
    DEAD_ZONE_X = 40
    DEAD_ZONE_Y = 40
    DEAD_ZONE_DISTANCE = 15

    ERROR_Y_OFFSET = 0 # Because of the angle of the camera the drone flys higher then it shoudld

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



def main_loop(tello: Tello, shared_qr: SharedQR):
    tello.takeoff()

    while True:
        qr = shared_qr.get()

        if qr == None:
            tello.send_rc_control(0, 0, 0, 0)    # zastav
            continue

        move_to_qr_code(tello, qr.error_xy.x, qr.error_xy.y, qr.distance_cm)

        text = (qr.text or "").lower()

        if qr.distance_cm < 60 and qr.distance_cm > 40:
            if text == "vlevo":
                tello.rotate_counter_clockwise(90)
            elif text == "vpravo":
                tello.rotate_clockwise(90)
            elif text == "přistát":
                tello.land()
            else:
                logger.error("Unknow QR Code message")

        



def start_flying_thread(tello: Tello, shared_qr: SharedQR):
    thread = threading.Thread(target=main_loop, args=(tello, shared_qr), daemon=True)
    thread.start()