import threading
from djitellopy import Tello



def main_loop(tello: Tello):
    tello.takeoff()
    tello.move_forward(50)



def start_flying_thread(tello: Tello):
    thread = threading.Thread(target=main_loop, args={tello: tello}, daemon=True)
    thread.start()