from __future__ import annotations
import subprocess
import cv2
from djitellopy import Tello
import threading
import time
import math
from typing import TYPE_CHECKING
from utils.Logger import logger
from utils.models import Corners, MouseData
from utils.errors import ConnectionError
from utils.color import C, colorful_battery, colorful_temperature
from config import IS_EMULATOR

if TYPE_CHECKING:
    from UI.elements.Element import Element


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
        logger.info("Skipping wifi check, because of emulator")
        return
    
    wifi = get_wifi_connection()
    if wifi is None:
        raise ConnectionError(f"{C.BOLD}Not conncted{C.RESET} to wifi")
    if not wifi.startswith("TELLO"):
        raise ConnectionError(f"Conncted to {C.BOLD}wrong wifi{C.RESET} - {wifi}")
    
    logger.info(f"WiFi connction: {C.BOLD}{wifi}{C.RESET}")


def is_mouse_in_bounding_box(mouse: MouseData, x1: int, y1: int, x2: int, y2: int) -> bool:
    return mouse.x >= x1 and mouse.x <= x2 and mouse.y >= y1 and mouse.y <= y2


def get_elements_bounding_box(elements: list[Element], include_nested: bool = False) -> tuple[int, int, int, int] | None:
    from UI.elements.Container import Container
    from UI.elements.Radio import RadioGroup
    bounds = []

    def collect(elements: list[Element]):
        for element in elements:
            if isinstance(element, Container):
                if include_nested:
                    collect(element.elements)
                continue

            if isinstance(element, RadioGroup):
                if include_nested:
                    collect(element.radios)
                continue

            bounds.append((element._x1, element._y1, element._x2, element._y2))

    collect(elements)

    if not bounds:
        return None

    return (
        min(bound[0] for bound in bounds),
        min(bound[1] for bound in bounds),
        max(bound[2] for bound in bounds),
        max(bound[3] for bound in bounds),
    )

def is_window_open(window_name: str) -> bool:
    try:
        return cv2.getWindowProperty(
            window_name,
            cv2.WND_PROP_VISIBLE,
        ) >= 1
    except cv2.error:
        return False
