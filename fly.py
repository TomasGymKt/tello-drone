import threading
import time
from djitellopy import TelloException

from shared import tello, shared_qr
from utils.Logger import logger
from settings import settings
from utils.models import QR_Code

# TODO: yaw control, if necessary

def get_xyz_move_cords(
    qr_code: QR_Code,
    deadzone_x_scale: float = 1.7,
    deadzone_y_scale: float = 1.25,
    left_right_step_scale: float = 1.7,
    forward_back_step_scale: float = 0.5,
    up_down_step_scale: float = 1.1,
) -> tuple[int, int, int]:
    """Calculate drone movement required to center and distance the QR code."""

    DISTANCE_FROM_CODE = 50  # cm

    DEADZONE_X = 180  # px
    DEADZONE_Y = 150  # px
    DEADZONE_DISTANCE = 0  # cm

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

    if deadzone_x > 150 or deadzone_y > 150:
        DEADZONE_DISTANCE = 150

    # Larger error -> larger step
    left_right_step = (BASE_STEP_SIZE * (abs(error_x) / ERROR_STEP_REFERENCE) ** left_right_step_scale)
    left_right_step = min(max(22, left_right_step), 40)
    up_down_step = (BASE_STEP_SIZE * (abs(error_y) / ERROR_STEP_REFERENCE) ** up_down_step_scale)
    up_down_step = min(max(20, up_down_step), 30)

    # Larger distance -> larger step
    forward_back_step = (BASE_DISTANCE_STEP_SIZE * distance_ratio ** forward_back_step_scale)
    forward_back_step = min(max(22, forward_back_step), 30)


    left_right = 0
    forward_back = 0
    up_down = 0

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

    if distance_error > DEADZONE_DISTANCE - 5:
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

def move_slowly_in_steps(xyz: tuple[int, int, int], duration: float, sleep: float = 0.7):
    forward_back, left_right, up_down = xyz
    a = "Forward" if forward_back > 0 else ("Back"  if forward_back < 0 else "")
    b = "Left"    if left_right > 0   else ("Right" if left_right < 0   else "")
    c = "Up"      if up_down > 0      else ("Down"  if up_down < 0      else "")
    logger.info(f"Moving {", ".join(filter(None, [a, b, c]))} for {duration}s")

    tello.send_rc_control(-left_right, forward_back, up_down, 0)
    time.sleep(duration)
    tello.send_rc_control(0, 0, 0, 0)
    time.sleep(sleep)

def move_in_1D(xyz: tuple[int, int, int]):
    forward_back, left_right, up_down = xyz

    axis = max(xyz, key=abs)

    if axis == 0:
        return


    if axis == left_right:
        if axis > 0:
            logger.info(f"Moving left {axis} cm")
            tello.move_left(axis)
        else:
            logger.info(f"Moving right {axis} cm")
            tello.move_right(-axis)

    elif axis == forward_back:
        if axis > 0:
            logger.info(f"Moving forward {axis} cm")
            tello.move_forward(axis)
        else:
            logger.info(f"Moving back {axis} cm")
            tello.move_back(-axis)

    elif axis == up_down:
        if axis > 0:
            logger.info(f"Moving up {axis} cm")
            tello.move_up(axis)
        else:
            logger.info(f"Moving down {axis} cm")
            tello.move_down(-axis)
    
    


def check_drone_height(allowed_variation: int = 30):
    current_height = tello.get_distance_tof()
    optimal = settings.optimal_drone_height
    delta = optimal - current_height

    if abs(delta) < max(allowed_variation, 25):
        return False
    
    if delta > 0:
        delta -= 5
        logger.info(f"Drone is too low ({current_height}cm/{optimal}cm), going up {delta}cm")
        tello.move_up(delta)
    else:
        delta = -delta - 5
        logger.info(f"Drone is too high ({current_height}cm/{optimal}cm), going down {delta}cm")
        tello.move_down(delta)
    return True

# Times: 213s, 158s, 167s, 132s, 202s, 132s, 160s, 162s, 140s, 148s, 132s, 173s, 108s

class FlyLoop:
    def __init__(self):
        self.last_seen_qr_at = 0
        self.last_valid_command = ""
        self.is_ready_for_execution = False
        self.last_distance_from_qr = 0

        self._first_qr = False
    
    def _handle_no_qr_v2(self, qr: QR_Code, velocity: int = 20, max_blind_time: float = 5):
        if qr == None or qr.distance_cm > 200:
            if not self._first_qr and time.perf_counter() - self.last_seen_qr_at > max_blind_time:
                logger.info(f"No QR Code detected for {max_blind_time}s, moving forward...")
                tello.send_rc_control(0, velocity, 0, 0)
                self._first_qr = True
            return
        self.last_seen_qr_at = time.perf_counter()
        
        if self._first_qr:
            logger.info("Detected a QR Code, stopped moving forward.")
            tello.send_rc_control(0, -20, 0, 0)
            time.sleep(0.5)
            tello.send_rc_control(0, 0, 0, 0)
            self._first_qr = False
    
    def _movement_strategy(self, qr: QR_Code, is_valid_command: bool):
        if qr.distance_cm < 60 and qr.distance_cm > 45:
            logger.success("Drone is in position to execute command")
            self.is_ready_for_execution = True
            return
        
        if qr.distance_cm < 80:
            time.sleep(0.5)

        xyz = get_xyz_move_cords(qr)
        
        if qr.distance_cm > 150:
            move_slowly_in_steps(xyz, 1, 1.0)
        elif qr.distance_cm > 120:
            move_slowly_in_steps(xyz, 0.7, 0.8)
        elif qr.distance_cm > 85:
            move_slowly_in_steps(xyz, 0.5)
        else:
            move_slowly_in_steps(xyz, 0.4)
        
    def _execute_command(self):
        command = self.last_valid_command
        
        if command == "vlevo":
            logger.success("Executing command: Rotate left")
            tello.rotate_counter_clockwise(90)
            logger.info("Adjusting for offset...")
            tello.send_rc_control(0, 65, 0, 0)
            time.sleep(2)
            tello.send_rc_control(30, 30, 0, 0)
            time.sleep(0.8)
            logger.info("   > Done")
            tello.send_rc_control(0, 0, 0, 0)
            
        elif command == "vpravo":
            logger.success("Executing command: Rotate right")
            # target_yaw = tello.get_yaw() + 90
            # if target_yaw > 180: target_yaw = -360 + target_yaw
            tello.rotate_clockwise(90)
            # logger.test(f"{target_yaw}  {tello.get_yaw()}")
            logger.info("Adjusting for offset...")
            tello.send_rc_control(0, 65, 0, 0)
            time.sleep(2)
            tello.send_rc_control(-30, 30, 0, 0) #Kdyz bude v zatacce litat moc doleva tak tohle upravit (prvni cislo - zapor znamena vic doleva)
            time.sleep(0.8)
            logger.info("   > Done")
            tello.send_rc_control(0, 0, 0, 0)
            
        elif command == "přistát":
            logger.success("Executing command: Land")
            tello.land()
            fly_worker.set_manual_control(True)
            
        else:
            logger.error("Unknow QR Code message")

    def loop(self):
        if check_drone_height():
            return

        qr = shared_qr.get()
        
        self._handle_no_qr_v2(qr)
        
        if qr == None:
            return
        
        self.last_distance_from_qr = qr.distance_cm
        
        text = (qr.text or "").lower()
        is_valid_command = text in ["vlevo", "vpravo", "přistát"]
        if is_valid_command: self.last_valid_command = text

        self._movement_strategy(qr, is_valid_command)
        
        if self.is_ready_for_execution:
            self._execute_command()
            
            self.is_ready_for_execution = False
            self.last_valid_command = ""



def setup_automatic():
    logger.info("Taking off...")
    tello.takeoff()
    logger.info("   > Done")

def hand_over_to_manual():
    if tello.is_flying:
        tello.land()

class FlyWorker:
    def __init__(self):
        self._condition = threading.Condition()
        self._is_running = False
        self._manual_control = True
        self._keep_alive = False
        self._last_keep_alive = time.perf_counter()

        self._manual_start_time = 0
        
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

            if enabled:
                logger.info(f"Was executing automatic sequence for {(time.time() - self._manual_start_time):.1f}s.")
            else:
                logger.info("Starting automatic sequnence")
                self._manual_start_time = time.time()

    def _worker_loop(self) -> None:
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

            try:
                self.fly_loop.loop()
            except TelloException as e:
                logger.error("An exeption occured in flying loop\n", e)

            if self._keep_alive and time.perf_counter() - self._last_keep_alive >= 8:
                logger.debug("Keep alive")
                tello.send_rc_control(0, 0, 0, 0)
                self._last_keep_alive = time.perf_counter()
            time.sleep(0.1)


fly_worker = FlyWorker()