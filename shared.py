from djitellopy import Tello
from settings import settings
from utils.models import SharedQR


tello = Tello(host=settings.ip_address)
shared_qr = SharedQR()