# this module is for stabilizing the speed of the car
# it controlls motor power through PWM to maintain constant cm/s speed
import rpigpioemul as GPIO
import time
import threading
from constants import IO_STABILIZER, STABILIZER_DELTA_MAX, STABILIZER_SMOOTHING, IO_DRIVE_P, IO_DRIVE_N
from .util import tickToCm, cmToTick, clamp, zeta
from .ticks import ticks
from state import broker
stabilizerThreadLock = threading.Lock()

def sign(x):
    return -1 if x < 0 else 1 
__active = False
__targetTPS = 80
__speed = 0
__deltaMax = STABILIZER_DELTA_MAX
__smoothing = STABILIZER_SMOOTHING
__dumpEnabled = False
__targetDirection = 0

dump_tps = []
dump_time = []
dump_target_tps = []
dump_power = []

GPIO.setmode(GPIO.BCM)
GPIO.setup(IO_STABILIZER, GPIO.OUT)
GPIO.setup(IO_DRIVE_P, GPIO.OUT)
GPIO.setup(IO_DRIVE_N, GPIO.OUT)

__pwm = GPIO.PWM(IO_STABILIZER, 120)
    
def config(deltaMax, smoothing, dump=False):
    global __deltaMax, __smoothing, __dumpEnabled
    __deltaMax = deltaMax
    __smoothing = smoothing
    __dumpEnabled = dump

def speed():
    return __speed
    
def stop():
    global __active, __pwm, stabilizerThreadLock
    with stabilizerThreadLock:
        if(not __active):
            __pwm.stop()
            GPIO.output(IO_STABILIZER, 0)
    __active = False

def start(cmPerSecond):
    global __targetTPS, __active, __targetDirection
    __targetTPS = cmToTick(abs(cmPerSecond)) 
    __targetDirection = sign(cmPerSecond)
    with stabilizerThreadLock:
        if(not __active):
            __pwm.start(0)
            __pwm.ChangeFrequency(120) 
    __active = True

def __stabilize():
    global stabilizerThreadLock, __speed, __targetDirection
    power = 50
    T = 0.1
    Y = 0.05
    while True:
        if not __active:
            power = 50
            if __speed != 0:
                broker.set('speed', 0)
                __speed = 0
            time.sleep(0.01)
            GPIO.output(IO_DRIVE_P, GPIO.LOW)
            GPIO.output(IO_DRIVE_N, GPIO.LOW)
            continue
        c = ticks()
        time.sleep(T)
        deltaCount = (ticks() - c)
        tps = deltaCount / T
        dif = tps - __targetTPS
        z = zeta(__smoothing, tps, __targetTPS) 
        
        if( dif < 0):
            power = power + __deltaMax*T * z
        elif dif > 0:
            power = power - __deltaMax*T * z
        power = clamp(power, 0, 100)
        with stabilizerThreadLock:
            __pwm.ChangeDutyCycle(power)
        s = tickToCm(tps)
        ds = s - __speed
        if (tps - __targetTPS ) > 25 and ds > 0:
            print('throttle')
            if __targetDirection > 0:
                # throttle backward
                GPIO.output(IO_DRIVE_P, GPIO.HIGH)
                GPIO.output(IO_DRIVE_N, GPIO.LOW)
            elif __targetDirection < 0:
                # throttle forward 
                GPIO.output(IO_DRIVE_P, GPIO.LOW)
                GPIO.output(IO_DRIVE_N, GPIO.HIGH)
        elif __targetDirection > 0:
            GPIO.output(IO_DRIVE_P, GPIO.LOW)
            GPIO.output(IO_DRIVE_N, GPIO.HIGH)
        else:
            GPIO.output(IO_DRIVE_P, GPIO.HIGH)
            GPIO.output(IO_DRIVE_N, GPIO.LOW)

        if abs(s - __speed) > 0.1:
            __speed = s
            broker.set('speed', __speed)
        if __dumpEnabled:
            dump_power.append(power)
            dump_tps.append(tps)
            dump_target_tps.append(__targetTPS)
            dump_time.append(time.time())
        T = clamp( 10/(tps+1e-36), 0.0001, 0.5)

stabilizerThread = threading.Thread(target=__stabilize)
stabilizerThread.daemon = True
stabilizerThread.start()