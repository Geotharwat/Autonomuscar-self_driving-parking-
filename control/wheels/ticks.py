# this module is for counting car wheel ticks through IR

import threading
import time
import rpigpioemul as GPIO
from constants import IO_INTRRUPTER
from state import broker

GPIO.setmode(GPIO.BCM)
GPIO.setup(IO_INTRRUPTER, GPIO.IN)

__lock = threading.Lock()
__ticks = 0


def __count():
    global __ticks, __lock
    while True:
        while GPIO.input(IO_INTRRUPTER) == 0:
            time.sleep(0.001)
        while GPIO.input(IO_INTRRUPTER) == 1:
            time.sleep(0.001)
        __ticks += 1
        broker.set('ticks', __ticks)
def ticks():
    return __ticks

counterThread = threading.Thread(target=__count)
counterThread.daemon = True
counterThread.start()
