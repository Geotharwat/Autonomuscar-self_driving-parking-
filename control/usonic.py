from ctypes import Union
import time
from typing import Optional
from constants import RPI
from navigation.typing import IProximity
import rpigpioemul as GPIO

GPIO.setmode(GPIO.BCM)


class USonic(IProximity):
    def __init__(self, trigger, echo, axis=0):
        super().__init__()
        self.trigger = trigger
        self.echo = echo
        self.last_m_time = 0
        self.last_m = None
        # set GPIO direction (IN / OUT)
        GPIO.setup(trigger, GPIO.OUT)
        GPIO.setup(echo, GPIO.IN)

    def distance(self) -> Optional[float]:
        # set Trigger to HIGH
        if time.time() - self.last_m_time < 0.05:
            return self.last_m
        self.last_m_time = time.time()
        GPIO.output(self.trigger, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)

        StartTime = time.time_ns()
        StopTime = time.time_ns()
        s = time.time()
        timeout = time.time_ns() + 8806910.25 * 2  # time for 300cm
        # save StartTime
        while GPIO.input(self.echo) == 0 and time.time_ns() < timeout:
            StartTime = time.time_ns()

        # save time of arrival
        while GPIO.input(self.echo) == 1 and time.time_ns() < timeout:
            StopTime = time.time_ns()

        if time.time_ns() > timeout:
            return None
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (3.406416e-5 cm/ns)
        # and divide by 2, because there and back
        self.last_m = (TimeElapsed * 3.406416e-5) / 2
        return self.last_m
