from djitellopy import Tello
from logger import logger
import threading
import time

def _log_stats(tello: Tello, period: int):
    while True:
        logger.info(
            "Battery: {}%        Temps: {}°C, {}°C"
            .format(tello.get_battery(), tello.get_lowest_temperature(), tello.get_highest_temperature())
        )
        time.sleep(period)

def start_periodic_stats_log(tello: Tello, period: int=10):
    thread = threading.Thread(target=_log_stats, args={tello: tello, period: period}, daemon=True)
    thread.start()