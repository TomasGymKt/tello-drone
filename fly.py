import threading
import time
from djitellopy import TelloException

from shared import tello, shared_qr
from utils.Logger import logger
from settings import settings
from utils.models import QR_Code

# TODO: zkusit létat jenom pomocí jedné dimenze s move_*(), nikoliv ve 3D s go_xyz_speed()
# připadá mi že dron je moc nestabilní ale při jednoduchých přikazech vypadá stabilní

# TODO: jak obejít step_size limit >> možná můžeme udělat 25 doprava a 20 doleva aby výsledek byl 5 doprava

# DONE: zkontolovat jestli x == dopředu/dozadu; y == doleva/doprava; z == nahoru/dolu
#   +x == forward, +y == left, +z == up
# IDEA asi ne: možná by dávalo smysl prohodit znaménko left_right v get_xyz_move_cords

# TODO: dynamický step_size nejlépe na zálkadě vzálenosti, teď je jenom: +20, 0, -20
# TODO: dynamický DEADZONEy

# TODO: yaw control, if necessary

def get_xyz_move_cords(
    qr_code: QR_Code,
    deadzone_x_scale: float = 1.7,
    deadzone_y_scale: float = 1.25,
    left_right_step_scale: float = 1.2,
    forward_back_step_scale: float = 1.0,
    up_down_step_scale: float = 0.8,
) -> tuple[int, int, int]:
    """Calculate drone movement required to center and distance the QR code."""

    DISTANCE_FROM_CODE = 50  # cm

    DEADZONE_X = 180  # px
    DEADZONE_Y = 150  # px
    DEADZONE_DISTANCE = 5  # cm

    ERROR_Y_OFFSET = 5  # px

    BASE_STEP_SIZE = 20
    BASE_DISTANCE_STEP_SIZE = 12
    ERROR_STEP_REFERENCE = 150  # px

    distance = qr_code.distance_cm
    error_x = qr_code.error_x
    error_y = qr_code.error_y - ERROR_Y_OFFSET

    # Distance ratio
    distance_ratio = distance / DISTANCE_FROM_CODE

    # Smaller distance -> larger deadzone
    deadzone_x = DEADZONE_X * (1 / distance_ratio) ** deadzone_x_scale
    deadzone_y = DEADZONE_Y * (1 / distance_ratio) ** deadzone_y_scale

    # Larger error -> larger step
    left_right_step = (BASE_STEP_SIZE * (abs(error_x) / ERROR_STEP_REFERENCE) ** left_right_step_scale)
    left_right_step = min(left_right_step, 40)
    up_down_step = (BASE_STEP_SIZE * (abs(error_y) / ERROR_STEP_REFERENCE) ** up_down_step_scale)
    up_down_step = min(up_down_step, 20)

    # Larger distance -> larger step
    forward_back_step = (BASE_DISTANCE_STEP_SIZE * distance_ratio ** forward_back_step_scale)
    forward_back_step = min(forward_back_step, 40)

    left_right_step   = 20
    forward_back_step = 20
    up_down_step      = 20

    left_right = 0
    forward_back = 0
    up_down = 0

    print(forward_back_step)

    # Left / right
    if error_x > deadzone_x:
        left_right = -round(left_right_step)
    elif error_x < -deadzone_x:
        left_right = round(left_right_step)

    # Up / down
    if error_y > deadzone_y:
        up_down = -round(up_down_step)
    elif error_y < -deadzone_y:
        up_down = round(up_down_step)

    # Forward / back
    distance_error = distance - DISTANCE_FROM_CODE

    if distance_error > DEADZONE_DISTANCE:
        forward_back = round(forward_back_step)
    elif distance_error < -DEADZONE_DISTANCE:
        forward_back = -round(forward_back_step)

    return (forward_back, left_right, up_down)

def move_continually(xyz: tuple[int, int, int]):
    """TODO DOCS

    need a `tello.send_rc_control(0, 0, 0, 0)` if qr code is None
    """
    
    forward_back, left_right, up_down = xyz
    tello.send_rc_control(
    -left_right,
    forward_back,
    up_down,
    0
    )
    
def move_in_steps(xyz: tuple[int, int, int], speed: int = 9):
    """TODO DOCS

    Args:
        TODO DOCS
        speed: The speed of the drone, >=9.
    """

    x, y, z = xyz
    tello.go_xyz_speed(x, y, z, speed)
    
    # time.sleep(5)

def move_slowly_in_steps(xyz: tuple[int, int, int], duration: float, sleep: float = 1.0):
    forward_back, left_right, up_down = xyz
    tello.send_rc_control(-left_right, forward_back, up_down, 0)
    time.sleep(duration)
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(sleep)

def move_in_1D(xyz: tuple[int, int, int]):
    forward_back, left_right, up_down = xyz

    axis = max(xyz, key=abs)

    if axis == 0:
        return

    # TODO: this function prioritizes going forward
    if axis == forward_back:
        if axis > 0:
            tello.move_forward(axis)
        else:
            tello.move_back(-axis)

    elif axis == left_right:
        if axis > 0:
            tello.move_right(axis)
        else:
            tello.move_left(-axis)

    elif axis == up_down:
        if axis > 0:
            tello.move_up(axis)
        else:
            tello.move_down(-axis)
    
    


def check_drone_height(allowed_variation: int = 30):
    current_height = tello.get_distance_tof()
    delta = settings.optimal_drone_height - current_height

    if abs(delta) < max(allowed_variation, 20):
        return False
    
    if delta > 0:
        tello.move_up(delta)
    else:
        tello.move_down(-delta)
    return True

# Times: 213s, 158s, 167s, 132s, 202s

class FlyLoop:
    def __init__(self):
        self.last_seen_qr_at = time.perf_counter()
        self.last_valid_command = ""
        self.is_ready_for_execution = False

    def _handle_no_qr(self, qr: QR_Code, max_blind_time: float = 5, extra_time: float = 2):
        if qr == None:
            # if a qr code is not seen in last max_blind_time seconds move forward
            # then every extra_time seconds move forward if still not seen
            if time.perf_counter() - self.last_seen_qr_at > max_blind_time:
                tello.move_forward(40)
                self.last_seen_qr_at += extra_time
        else:
            self.last_seen_qr_at = time.perf_counter()
    
    def _movement_strategy(self, qr: QR_Code, is_valid_command: bool):
        if qr.distance_cm < 60 and qr.distance_cm > 40:
            self.is_ready_for_execution = True
            return

        xyz = get_xyz_move_cords(qr)
        
        if qr.distance_cm > 120:
            move_in_steps(xyz)
        # elif qr.distance_cm > 100:
        #     move_in_1D(xyz)
        elif qr.distance_cm > 80:
            move_slowly_in_steps(xyz, 0.5)
        else:
            move_slowly_in_steps(xyz, 0.4)
        
    def _execute_command(self):
        command = self.last_valid_command
        
        if command == "vlevo":
            logger.success("Rotating left")
            tello.rotate_counter_clockwise(90)
            tello.move_forward(60)
            tello.move_right(50)
            
        elif command == "vpravo":
            logger.success("Rotating right")
            tello.rotate_clockwise(90)
            tello.move_forward(60)
            tello.move_left(25)
            
        elif command == "přistát":
            logger.success("Landing")
            tello.land()
            fly_worker.set_manual_control(True)
            
        else:
            logger.error("Unknow QR Code message")

    def loop(self):
        if check_drone_height():
            return

        qr = shared_qr.get()
        
        self._handle_no_qr(qr)
        
        if qr == None:
            return
        
        text = (qr.text or "").lower()
        is_valid_command = text in ["vlevo", "vpravo", "přistát"]
        if is_valid_command: self.last_valid_command = text

        self._movement_strategy(qr, is_valid_command)
        
        if self.is_ready_for_execution:
            self._execute_command()
            
            self.is_ready_for_execution = False
            self.last_valid_command = ""



def setup_automatic():
    tello.takeoff()

def hand_over_to_manual():
    if tello.is_flying:
        tello.land()

class FlyWorker:
    def __init__(self):
        self._condition = threading.Condition()
        self._is_running = False
        self._manual_control = True
        self._keep_alive = True
        self._last_keep_alive = time.perf_counter()
        
        self.fly_loop = FlyLoop()

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
        self.fly_loop.last_seen_qr_at = time.perf_counter() # TODO: idk if necessary
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
                self.fly_loop.last_seen_qr_at = time.perf_counter() # TODO: idk if necessary
                continue

            try:
                self.fly_loop.loop()
            except TelloException as e:
                logger.error("An exeption occured in flying loop\n", e)

            if self._keep_alive and time.perf_counter() - self._last_keep_alive >= 8:
                tello.send_rc_control(0, 0, 0, 0)
                self._last_keep_alive = time.perf_counter()
            time.sleep(0.1)


fly_worker = FlyWorker()