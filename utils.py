from djitellopy import Tello
from logger import logger
import threading
import time
import cv2
import zxingcpp
import math
from config import QR_CODE_SIZE_CM, CAMERA_FOCAL_LENGTH_PX


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


def qr_size(points: list[tuple[int, int]]) -> float:
  top = math.dist(points[0], points[1])
  right = math.dist(points[1], points[2])
  bottom = math.dist(points[2], points[3])
  left = math.dist(points[3], points[0])

  return (top + right + bottom + left) / 4


def draw_cernter_cross(frame, cross_size = 5):
    frame_height, frame_width = frame.shape[:2]

    screen_center_x = frame_width // 2
    screen_center_y = frame_height // 2

    cv2.line(
    frame,
    (screen_center_x - cross_size, screen_center_y),
    (screen_center_x + cross_size, screen_center_y),
    (0, 0, 255),
    2
    )

    cv2.line(
    frame,
    (screen_center_x, screen_center_y - cross_size),
    (screen_center_x, screen_center_y + cross_size),
    (0, 0, 255),
    2
    )


def get_qr_code(frame, scale: int=1):
    frame_height, frame_width = frame.shape[:2]

    screen_center_x: int = frame_width // 2
    screen_center_y: int = frame_height // 2

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    small = cv2.resize(gray, None, fx=1 / scale, fy=1 / scale)
    results = zxingcpp.read_barcodes(small)

    if len(results) == 0:
        return None
    
    result = results[0]
    
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

    center_x = sum(x for x, _ in points) // 4
    center_y = sum(y for _, y in points) // 4

    size = qr_size(points)
    distance_cm = (QR_CODE_SIZE_CM * CAMERA_FOCAL_LENGTH_PX) / size

    error_x = center_x - screen_center_x
    error_y = center_y - screen_center_y

    return points, text, (center_x, center_y), size, distance_cm, (error_x, error_y)


def draw_qrcodes(frame, scale: int=1):
    frame_height, frame_width = frame.shape[:2]

    screen_center_x = frame_width // 2
    screen_center_y = frame_height // 2

    qr_code = get_qr_code(frame, scale)
    if qr_code == None:
        return
    points, text, (center_x, center_y), size, distance_cm, (error_x, error_y) = qr_code

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


    cv2.putText(
    frame,
    f"size: {int(size)} | dist: ${distance_cm:.1f} cm",
    (points[0][0], points[0][1] - 35),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.7,
    (0, 255, 0),
    2
    )

    # Čára mezi středem obrazovky a QR
    cv2.line(
    frame,
    (screen_center_x, screen_center_y),
    (center_x, center_y),
    (255, 0, 0),
    2
    )



    text = f"dx:{error_x} dy:{error_y}"

    (text_width, text_height), _ = cv2.getTextSize(
    text,
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    2
    )

    text_x = (screen_center_x + center_x) // 2 - text_width // 2
    text_y = (screen_center_y + center_y) // 2 + text_height // 2

    cv2.putText(
    frame,
    text,
    (text_x, text_y),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (255, 0, 0),
    2
    )
