import math
from constants import WHEEL_RADIUS, TICKS_PER_WHEEL

def cmToTick(cm):
    cmpt = (2 * math.pi * WHEEL_RADIUS) / TICKS_PER_WHEEL
    return cm / cmpt

def tickToCm(ticks):
    tpcm = TICKS_PER_WHEEL/ (2 * math.pi * WHEEL_RADIUS) 
    return ticks / tpcm


def clamp(v, min, max):
    return max if v > max else min if v < min else v

def zeta(smoothing, current, target):
    # refer https://www.desmos.com/calculator/k84rfvhfjx
    d = math.pow(abs( target -current ), 1 + smoothing) 
    return d / (target + d)