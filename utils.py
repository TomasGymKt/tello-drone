from djitellopy import Tello
from logger import logger
import threading
import time


def colorful_battery(percentage: int):
    """returns {percentage}% with color"""
    
    colors = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46]
    index = min(len(colors) - 1, percentage // 10)

    return f"\033[38;5;{colors[index]}m{percentage}%\033[0m"

def colorful_temperature(temp: int):
    """returns {temp}°C with color"""
    if temp < 35:
        return f"\033[92m{temp}°C\033[0m"  # red
    elif temp < 45:
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
