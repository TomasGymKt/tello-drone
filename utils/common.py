from __future__ import annotations
from collections import deque
from functools import wraps
import subprocess
import cv2
from djitellopy import Tello
import threading
import time
from typing import TYPE_CHECKING

import numpy as np
from utils.Logger import logger
from utils.errors import ConnectionError
from utils.color import C, colorful_battery, colorful_temperature

if TYPE_CHECKING:
    from utils.models import MouseData
    from UI.elements.Element import Element


def _log_stats(tello: Tello, period: int):
    """
    internal function, you don't normally call this
    logs the current battery percentage and min, max temperature in a colorful format
    """
    
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
    """
    starts asynchronously logging battery percentage and min, max temperature in a colorful format
    """
    
    thread = threading.Thread(target=_log_stats, args=(tello, period), daemon=True)
    thread.start()



def get_wifi_connection() -> str | None:
    """
    searches for a wifi connection and return it's name or None if it didn't find any
    """
    
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
    """
    raises an ConnectonError if not connected to wifi
    raises an ConnectonError if a simple wifi name check fails
    """
    
    from settings import settings
    if settings.is_emulator:
        logger.info("Skipping wifi check, because of emulator")
        return
    
    wifi = get_wifi_connection()
    if wifi is None:
        raise ConnectionError(f"{C.BOLD}Not conncted{C.RESET} to wifi")
    if not wifi.startswith("TELLO"):
        raise ConnectionError(f"Conncted to {C.BOLD}wrong wifi{C.RESET} - {wifi}")
    
    logger.info(f"WiFi connction: {C.BOLD}{wifi}{C.RESET}")

def create_blank_frame(width: int, height: int, color: tuple[int, int, int] = (255, 255, 255)):
    """
    returns a frame with width and height
    """
    
    frame = np.full((width, height, 3), color, dtype=np.uint8)
    return frame


def is_mouse_in_bounding_box(mouse: MouseData, x1: int, y1: int, x2: int, y2: int) -> bool:
    """
    returns if a mouse is in a bounding box
    """
    
    return mouse.x >= x1 and mouse.x <= x2 and mouse.y >= y1 and mouse.y <= y2


def get_elements_bounding_box(elements: list[Element], include_nested: bool = False) -> tuple[int, int, int, int] | None:
    """
    returns a bounding box from the elements or None if no valid element is provided
    if include_nested is set to True it finds the bound recursively
    
    recommened only for debuging
    """
    
    from UI.elements.Container import Container
    from UI.elements.Radio import RadioGroup
    from UI.elements.Shapes import Circle
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

            if isinstance(element, Circle):
                bounds.append((element._x-element._radius, element._y-element._radius, element._x+element._radius, element._y+element._radius))
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
    """
    returns if an window is opend
    """
    
    try:
        return cv2.getWindowProperty(
            window_name,
            cv2.WND_PROP_VISIBLE,
        ) >= 1
    except cv2.error:
        return False


def timer(print_interval=0, highest=3, lowest=3):
    """
    a decorator function that times a function across time
    """

    def decorator(func):
        times = deque(maxlen=16)
        last_print = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_print

            start = time.perf_counter()

            result = func(*args, **kwargs)

            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
            now = time.perf_counter()

            if now - last_print >= print_interval:
                sorted_times = sorted(times)

                minimum = sorted_times[0]
                maximum = sorted_times[-1]
                average = sum(times) / len(times)

                lowest_avg = sum(sorted_times[:lowest]) / min(lowest, len(times))
                highest_avg = sum(sorted_times[-highest:]) / min(highest, len(times))

                logger.debug(
                    f"{C.DIM     }Timer{C.RESET} '{func.__name__}' | "
                    f"{C.FG_RED  }Min: {minimum:7.3f} ms{C.RESET} | "
                    f"{C.FG_GREEN}Max: {maximum:7.3f} ms{C.RESET} | "
                    f"{C.FG_BLUE }Avg: {average:7.3f} ms{C.RESET} {C.DIM}| "
                    f"{C.FG_RED  }Bottom {lowest} avg: {lowest_avg:7.3f} ms{C.FG_WHITE} | "
                    f"{C.FG_GREEN}Top {highest} avg: {highest_avg:7.3f} ms{C.RESET}"
                )

                last_print = now

            return result
        return wrapper
    return decorator