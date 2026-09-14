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

# TODO: zkontolovat jestli x == dopředu/dozadu; y == doleva/doprava; z == nahoru/dolu
# TODO: možná by dávalo smysl prohodit znaménko left_right v get_xyz_move_cords

# TODO: dynamický step_size nejlépe na zálkadě vzálenosti, teď je jenom: +20, 0, -20
# TODO: dynamický DEADZONEy

# TODO: yaw control, if necessary

def get_xyz_move_cords(qr_code: QR_Code, step_size: int = 20) -> tuple[int, int, int]:
    """TODO DOCS

    Args:
        qr_code: The QR Code to move to
        step_size: The size of steps the drone flys, in cm, >=20.
    """
    DISTANCE_FROM_CODE = 50 # cm

    DEADZONE_X = 40 # px
    DEADZONE_Y = 40 # px
    DEADZONE_DISTANCE = 5 # px

    ERROR_Y_OFFSET = 5 # px; Because of the angle of the camera the drone flys higher then it shoudld

    error_y = qr_code.error_y
    error_y -= ERROR_Y_OFFSET

    left_right = 0
    forward_back = 0
    up_down = 0
    
    if step_size < 20:
        logger.error(f"Step size is too small. Minimum value: {20}; current value: {step_size}")
        return

    # Vlevo / vpravo
    if qr_code.error_x > DEADZONE_X:
        left_right = -step_size
    elif qr_code.error_x < -DEADZONE_X:
        left_right = step_size

    # Nahoru / dolů
    if error_y > DEADZONE_Y:
        up_down = -step_size
    elif error_y < -DEADZONE_Y:
        up_down = step_size

    # Vzdálenost od QR
    distance_error = qr_code.distance_cm - DISTANCE_FROM_CODE

    if distance_error > DEADZONE_DISTANCE:
        forward_back = step_size
    elif distance_error < -DEADZONE_DISTANCE:
        forward_back = -step_size
    
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

def move_slowly_in_steps(xyz: tuple[int, int, int]):
    forward_back, left_right, up_down = xyz
    tello.send_rc_control(-left_right, forward_back, up_down, 0)
    time.sleep(0.5) # TODO: adjust
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(0.8) # TODO: adjust

def move_in_1D(xyz: tuple[int, int, int]):
    forward_back, left_right, up_down = xyz

    axis = max(xyz, key=abs)

    if axis == 0:
        return

    if axis == forward_back:
        if axis > 0:
            tello.move_forward(-axis) # TODO: I don't know if the negative sign is flipped like with rc_control 
        else:
            tello.move_back(axis)

    elif axis == left_right:
        if axis > 0:
            tello.move_right(axis)
        else:
            tello.move_left(-axis)

    else:
        if axis > 0:
            tello.move_up(axis)
        else:
            tello.move_down(-axis)
    
    


def check_drone_height(allowed_variation: int = 30):
    current_height = tello.get_distance_tof()
    if current_height < settings.min_flying_height - 10:
        tello.move_up(max(settings.min_flying_height - current_height, 20))
        return

    delta = settings.optimal_drone_height - current_height

    if abs(delta) < max(allowed_variation, 20):
        return
    
    if delta > 0:
        tello.move_up(delta)
    else:
        tello.move_down(-delta)

class FlyLoop:
    def __init__(self):
        self.last_seen_qr_at = time.perf_counter()
        self.last_valid_command = ""
        self.is_ready_for_execution = False

    def _handle_no_qr(self, qr: QR_Code, max_blind_time: float = 10, extra_time: float = 2):
        if qr == None:
            # if a qr code is not seen in last max_blind_time seconds move forward
            # then every extra_time seconds move forward if still not seen
            if time.perf_counter() - self.last_seen_qr_at > max_blind_time:
                tello.move_forward(35)                          
                self.last_seen_qr_at += extra_time
        else:
            self.last_seen_qr_at = time.perf_counter()
    
    def _movement_strategy(self, qr: QR_Code, is_valid_command: bool):
        xyz = get_xyz_move_cords(qr)
        
        if qr.distance_cm > 150:
            move_in_steps(xyz)
        elif qr.distance_cm > 100:
            move_in_1D(xyz)
        else:
            move_slowly_in_steps(xyz)
        
    def _execute_command(self):
        command = self.last_valid_command
        
        if command == "vlevo":
            logger.success("Rotating left")
            tello.rotate_counter_clockwise(90)
            
        elif command == "vpravo":
            logger.success("Rotating right")
            tello.rotate_clockwise(90)
            
        elif command == "přistát":
            logger.success("Landing")
            tello.land()
            
        else:
            logger.error("Unknow QR Code message")

    def loop(self):
        check_drone_height()

        qr = shared_qr.get()
        
        self._handle_no_qr(qr)
        
        if qr == None:
            return
        
        text = (qr.text or "").lower()
        is_valid_command = text in ["vlevo", "vpravo", "přistát"]
        if is_valid_command: self.last_valid_command = text

        self._movement_strategy(qr, is_valid_command)
        
        if qr.distance_cm < 60 and qr.distance_cm > 40: # TODO: move this into movement_strategy
            self.is_ready_for_execution = True
        
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