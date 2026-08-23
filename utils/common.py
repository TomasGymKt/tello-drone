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
    """Continuously log battery and temperature information.

    Args:
        tello: Connected drone used to read telemetry.
        period: Delay between telemetry logs in seconds.
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
    """Start a daemon thread that logs drone telemetry periodically.

    Args:
        tello: Connected drone used to read telemetry.
        period: Delay between telemetry logs in seconds.
    """
    
    thread = threading.Thread(target=_log_stats, args=(tello, period), daemon=True)
    thread.start()



def get_wifi_connection() -> str | None:
    """Return the active physical Wi-Fi profile name.

    Returns:
        Connected Wi-Fi name, or None when no physical Wi-Fi is connected.

    Raises:
        Exception: If multiple physical Wi-Fi profiles are active.
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
    """Validate the Tello Wi-Fi connection unless emulator mode is active.

    Raises:
        ConnectionError: If Wi-Fi is disconnected or not a Tello network.
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
    """Create a solid BGR OpenCV image.

    Args:
        width: Frame width in pixels.
        height: Frame height in pixels.
        color: BGR fill color.

    Returns:
        New uint8 OpenCV image filled with color.
    """
    
    frame = np.full((width, height, 3), color, dtype=np.uint8)
    return frame


def is_mouse_in_bounding_box(mouse: MouseData, x1: int, y1: int, x2: int, y2: int) -> bool:
    """Check whether a pointer lies inside inclusive rectangle bounds.

    Args:
        mouse: Pointer coordinates to test.
        x1: Left bound.
        y1: Top bound.
        x2: Right bound.
        y2: Bottom bound.

    Returns:
        True when the pointer is inside or on the rectangle boundary.
    """
    
    return mouse.x >= x1 and mouse.x <= x2 and mouse.y >= y1 and mouse.y <= y2


def get_elements_bounding_box(elements: list[Element], include_nested: bool = False) -> tuple[int, int, int, int] | None:
    """Calculate bounds around drawable elements for debug rendering.

    Args:
        elements: Elements whose geometry is inspected.
        include_nested: Whether to descend into containers and radio groups.

    Returns:
        Left, top, right, and bottom bounds, or None when no geometry exists.
    """
    
    from UI.elements.Container import Container
    from UI.elements.Radio import RadioGroup
    from UI.elements.Shapes import Circle
    bounds = []

    def collect(elements: list[Element]):
        """Recursively collect drawable bounds from an element sequence.

        Args:
            elements: Elements to inspect at the current nesting level.
        """
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
    """Check whether an OpenCV window is still visible.

    Args:
        window_name: Title of the window to inspect.

    Returns:
        True when the window is visible; False for missing or closed windows.
    """
    
    try:
        return cv2.getWindowProperty(
            window_name,
            cv2.WND_PROP_VISIBLE,
        ) >= 1
    except cv2.error:
        return False


def timer(print_interval=0, highest=3, lowest=3):
    """Create a decorator that logs rolling execution-time statistics.

    Args:
        print_interval: Minimum seconds between statistic log messages.
        highest: Number of slowest samples included in the high average.
        lowest: Number of fastest samples included in the low average.

    Returns:
        Decorator that wraps a callable with timing instrumentation.
    """

    def decorator(func):
        """Wrap a callable with rolling timing measurements.

        Args:
            func: Callable to instrument.

        Returns:
            Callable that preserves the original result after recording duration.
        """
        times = deque(maxlen=16)
        last_print = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            """Call the wrapped function and record its execution duration.

            Args:
                *args: Positional arguments forwarded to the wrapped callable.
                **kwargs: Keyword arguments forwarded to the wrapped callable.

            Returns:
                Result returned by the wrapped callable.
            """
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
                    f"{C.RED  }Min: {minimum:7.3f} ms{C.RESET} | "
                    f"{C.GREEN}Max: {maximum:7.3f} ms{C.RESET} | "
                    f"{C.BLUE }Avg: {average:7.3f} ms{C.RESET} {C.DIM}| "
                    f"{C.RED  }Bottom {lowest} avg: {lowest_avg:7.3f} ms{C.WHITE} | "
                    f"{C.GREEN}Top {highest} avg: {highest_avg:7.3f} ms{C.RESET}"
                )

                last_print = now

            return result
        return wrapper
    return decorator
