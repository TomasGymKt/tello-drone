import subprocess
from djitellopy import Tello
import threading
import time
import math
from utils.logger import logger
from utils.models import Corners
from utils.errors import ConnectionError
from utils.color import C, colorful_battery, colorful_temperature
from draw import draw_info
from config import IS_EMULATOR



def _log_stats(tello: Tello, period: int):
    while True:
        logger.info(
            "Battery: {}        Temps: {}, {}"
            .format(
                colorful_battery(tello.get_battery()),
                colorful_temperature(tello.get_lowest_temperature()),
                colorful_temperature(tello.get_highest_temperature())
            )
        )
        time.sleep(period)

def start_periodic_stats_log(tello: Tello, period: int=10) -> None:
    thread = threading.Thread(target=_log_stats, args=(tello, period), daemon=True)
    thread.start()


def qr_size(points: Corners) -> float:
    top = math.dist(points.top_left, points.top_right)
    right = math.dist(points.top_right, points.bottom_right)
    bottom = math.dist(points.bottom_right, points.bottom_left)
    left = math.dist(points.bottom_left, points.top_left)

    return (top + right + bottom + left) / 4



def distance(a, b):
    return math.hypot(
        a[0] - b[0],
        a[1] - b[1]
    )


class FPSCounter:
    pos_x = 7
    pos_y = 25
    opacity = 0.5
    color = (0, 255, 0)
    
    fontSize = 0.6
    fontThickness = 1
    
    count = -1
    
    
    def __init__(self, decay=1.5, pos_x=pos_x, pos_y=pos_y, opacity=opacity, fontSize=fontSize, fontThickness=fontThickness):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.opacity = opacity
        self.fontSize = fontSize
        self.fontThickness = fontThickness
        
        self.last_time = time.time()
        self.fps = -1
        
        self.decay = decay
        self.init_time = time.time()
        

    def update(self) -> tuple[float, int]:
        current_time = time.time()
        
        # Don't update the FPS until the decay fades away
        if current_time - self.decay < self.init_time:
            self.last_time = current_time
            return self.fps, self.count
        
        
        self.count += 1

        instant_fps = 1 / (current_time - self.last_time)

        # Set the starting FPS
        if self.count == 2:
            self.fps = instant_fps
            self.last_time = current_time
            return self.fps, self.count
        
        self.fps = self.fps * 0.7 + instant_fps * 0.3
        self.last_time = current_time

        return self.fps, self.count
    
    def draw(self, frame) -> None:
        text = f"FPS: {self.fps:.1f}"
        
        draw_info(frame, text, self.pos_x, self.pos_y, self.color, opacity=self.opacity, fontSize=self.fontSize, fontThickness=self.fontThickness)


class FrameTracker:
    def __init__(self):
        self._last_frame_id = None

    def is_new_frame(self, frame) -> bool:
        frame_id = id(frame)

        if frame_id == self._last_frame_id:
            return False

        self._last_frame_id = frame_id
        return True



def get_wifi_connection() -> str | None:
    ssids = subprocess.check_output(
        [
            "powershell",
            "-Command",
            "(Get-NetAdapter -Physical | Where-Object {$_.Status -eq 'Up' -and $_.InterfaceDescription -match 'Wireless|Wi-Fi|802.11'} | Get-NetConnectionProfile).Name"
        ],
        text=True
    ).strip().splitlines()
    
    if len(ssids) > 1:
        raise Exception("Multiple Wi-Fi connections")
    
    if len(ssids) == 0:
        return None
    
    return ssids[0].split(" ")[0]

def check_wifi():
    if IS_EMULATOR:
        logger.info("Skipping wifi chek, because of emulator")
        return
    
    wifi = get_wifi_connection()
    if wifi is None:
        raise ConnectionError(f"{C.BOLD}Not conncted{C.RESET} to wifi")
    if not wifi.startswith("TELLO"):
        raise ConnectionError(f"Conncted to {C.BOLD}wrong wifi{C.RESET} - {wifi}")
    
    logger.info(f"WiFi connction: {wifi}")
