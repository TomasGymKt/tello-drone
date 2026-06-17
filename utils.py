from djitellopy import Tello
from logger import logger
import threading
import time
import cv2
import zxingcpp


def colorful_battery(percentage: int):
    """returns {percentage}% with color"""
    
    colors = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46]
    index = min(len(colors) - 1, percentage // 10)

    return f"\033[38;5;{colors[index]}m{percentage}%\033[0m"

def colorful_temperature(temp: int):
    """returns {temp}°C with color"""
    if temp < 82:
        return f"\033[92m{temp}°C\033[0m"  # red
    elif temp < 88:
        return f"\033[93m{temp}°C\033[0m"  # yellow
    else:
        return f"\033[91m{temp}°C\033[0m"  # green




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

def start_periodic_stats_log(tello: Tello, period: int=10):
    thread = threading.Thread(target=_log_stats, args={tello: tello, period: period}, daemon=True)
    thread.start()


def draw_qrcodes(frame, scale: int=1):
    small = cv2.resize(frame, None, fx=1 / scale, fy=1 / scale)
    results = zxingcpp.read_barcodes(small)

    for result in results:
        text = result.text

        points = [
            (
            int(result.position.top_left.x * scale),
            int(result.position.top_left.y * scale)
            ),
            (
            int(result.position.top_right.x * scale),
            int(result.position.top_right.y * scale)
            ),
            (
            int(result.position.bottom_right.x * scale),
            int(result.position.bottom_right.y * scale)
            ),
            (
            int(result.position.bottom_left.x * scale),
            int(result.position.bottom_left.y * scale)
            ),
        ]

        # QR outline
        for i in range(4):
            cv2.line(
            frame,
            points[i],
            points[(i + 1) % 4],
            (0, 255, 0),
            2
            )

        # Center
        center_x = sum(x for x, _ in points) // 4
        center_y = sum(y for _, y in points) // 4

        cv2.circle(
            frame,
            (center_x, center_y),
            5,
            (0, 0, 255),
            -1
        )

        # Text
        cv2.putText(
            frame,
            text,
            (points[0][0], points[0][1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
