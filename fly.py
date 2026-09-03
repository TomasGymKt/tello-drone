import threading
import time

from shared import tello, shared_qr
from utils.Logger import logger
from settings import settings

def move_to_qr_code(error_x: int, error_y: int, distance_cm: float, SPEED: int=20):
    """Send drone movement commands that center on and approach a QR code.

    Args:
        error_x: QR horizontal offset from the camera center in pixels.
        error_y: QR vertical offset from the camera center in pixels.
        distance_cm: Estimated distance from the QR code in centimeters.
        SPEED: Absolute RC speed used outside configured dead zones.
    """
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
    
def move_to_qr_code_in_steps(error_x: int, error_y: int, distance_cm: float, step_size: int=20, speed: int=10):
    """Send drone movement commands that center on and approach a QR code.

    Args:
        error_x: QR horizontal offset from the camera center in pixels.
        error_y: QR vertical offset from the camera center in pixels.
        distance_cm: Estimated distance from the QR code in centimeters.
    """
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
        left_right = step_size
    elif error_x < -DEAD_ZONE_X:
        left_right = -step_size

    # Nahoru / dolů
    if error_y > DEAD_ZONE_Y:
        up_down = -step_size
    elif error_y < -DEAD_ZONE_Y:
        up_down = step_size

    # Vzdálenost od QR
    distance_error = distance_cm - 50

    if distance_error > DEAD_ZONE_DISTANCE:
        forward_back = step_size
    elif distance_error < -DEAD_ZONE_DISTANCE:
        forward_back = -step_size

    tello.go_xyz_speed(forward_back, left_right, up_down, speed)
    time.sleep(0.5)
    timestamp = time.time()
    responses = tello.get_own_udp_object()['responses']
    while not responses:
        if time.time() - timestamp > 10:
            print("timedout")
        time.sleep(0.1)  # Sleep during send command

    

def setup_automatic():
    tello.takeoff()

def hand_over_to_manual():
    tello.land()

def loop():
    qr = shared_qr.get()

    if qr == None:
        tello.send_rc_control(0, 0, 0, 0)    # zastav
        return


    move_to_qr_code_in_steps(qr.error_x, qr.error_y, qr.distance_cm)

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



class FlyWorker:
    def __init__(self):
        self._condition = threading.Condition()
        self._is_running = False
        self._manual_control = False

        self._thread: threading.Thread | None = None

    @property
    def manual_control(self) -> bool:
        with self._condition:
            return self._manual_control

    def start(self) -> None:
        with self._condition:
            if self._is_running:
                return

            self._is_running = True

            self._thread = threading.Thread(
                target=self._worker_loop,
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        with self._condition:
            if not self._is_running:
                return

            self._is_running = False
            self._condition.notify_all()

        self._thread.join(timeout=1)
        self._thread = None

    def set_manual_control(self, enabled: bool) -> None:
        with self._condition:
            if self._manual_control == enabled:
                return

            self._manual_control = enabled
            self._condition.notify_all()

    def _worker_loop(self) -> None:
        setup_automatic()

        while True:
            with self._condition:
                if not self._is_running:
                    return

                manual_control = self._manual_control

            if manual_control:
                hand_over_to_manual()

                with self._condition:
                    while self._manual_control and self._is_running:
                        self._condition.wait()

                    if not self._is_running:
                        return

                setup_automatic()
                continue

            loop()


fly_worker = FlyWorker()