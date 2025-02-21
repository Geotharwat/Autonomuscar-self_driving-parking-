import threading
from constants import IO_STEER_P, IO_STEER_N, IO_DRIVE_P, IO_DRIVE_N, MODE_IDLE
import time
import atexit
import rpigpioemul as GPIO
from .ticks import ticks
from .stabilizer import start as startStabilizer, stop as stopStabilizer
from .util import cmToTick, tickToCm
from state import getMode

GPIO.setmode(GPIO.BCM)
GPIO.setup(IO_STEER_P, GPIO.OUT)
GPIO.setup(IO_STEER_N, GPIO.OUT)


GPIO.output(IO_DRIVE_N, GPIO.LOW)
GPIO.output(IO_STEER_N, GPIO.LOW)
GPIO.output(IO_DRIVE_P, GPIO.LOW)
GPIO.output(IO_STEER_P, GPIO.LOW)

# GPIO.output(DRIVE_PWM, GPIO.HIGH)

lastDir = 0

drive_start = 0


__active = False

__state_drive = 0
__state_steer = 0



def drive(speed):
    global lastDir, drive_start, __state_drive
    __state_drive = speed
    if speed == 0:
        stopStabilizer()
    else:
        startStabilizer(speed)
 
    # if speed == 0:
    #     GPIO.output(IO_DRIVE_P, GPIO.LOW)
    #     GPIO.output(IO_DRIVE_N, GPIO.LOW)
    #     stopStabilizer()
    # elif speed > 0:
    #     GPIO.output(IO_DRIVE_P, GPIO.LOW)
    #     GPIO.output(IO_DRIVE_N, GPIO.HIGH)
    #     startStabilizer(abs(speed))
    # else:
    #     GPIO.output(IO_DRIVE_P, GPIO.HIGH)
    #     GPIO.output(IO_DRIVE_N, GPIO.LOW)
    #     startStabilizer(abs(speed))

def getState(): 
    global __state_drive, __state_steer
    return (__state_drive, __state_steer)

__prev_steer = 0
def steerPerfect(dir=0):
    global __prev_steer
    steer(-__prev_steer)
    time.sleep(0.1)
    steer(dir)
    __prev_steer = dir

def steer(dir=0):
    global __state_drive
    __state_drive = dir
    if dir == 0:
        GPIO.output(IO_STEER_P, GPIO.LOW)
        GPIO.output(IO_STEER_N, GPIO.LOW)
    elif dir > 0:
        GPIO.output(IO_STEER_P, GPIO.LOW)
        GPIO.output(IO_STEER_N, GPIO.HIGH)
    else:
        GPIO.output(IO_STEER_P, GPIO.HIGH)
        GPIO.output(IO_STEER_N, GPIO.LOW)


def brake(lastSpeed):
    prev = ticks()
    for i in range(100):
        if ticks() != prev:
            break
        time.sleep(0.001)
        if getMode() ==  MODE_IDLE:
            drive(0)
            steer(0)
            return False
    while ticks() != prev:
        prev = ticks()
        drive(-lastSpeed)
        time.sleep(0.025)
        if getMode() == MODE_IDLE:
            drive(0)
            steer(0)
            return False
    drive(0)


def move(speed, steering, distance):
    steer(steering)
    drive(speed)
    s = ticks()
    target = cmToTick(distance)
    while ticks() - s < target:
        time.sleep(0.1)
        if getMode() == MODE_IDLE:
            drive(0)
            steer(0)
            return False
    drive(0)
    return True


def moveExact(speed, steering, distance):
    print(f"start-ticks={ticks()}")
    if not move(speed, steering, distance):  # if interrupted
        drive(0)
        steer(0)
        return False
    s = ticks()
    brake(speed)
    extra = ticks() - s
    if not move(-speed, steering, tickToCm(extra)):  # if interrupted
        drive(0)
        steer(0)
        return False
    brake(-speed)
    steer(0)
    print(f"end-ticks={ticks()}")


def exit_handler():
    GPIO.output(IO_DRIVE_N, GPIO.LOW)
    GPIO.output(IO_STEER_N, GPIO.LOW)
    GPIO.output(IO_DRIVE_P, GPIO.LOW)
    GPIO.output(IO_STEER_P, GPIO.LOW)
    GPIO.cleanup()


atexit.register(exit_handler)
