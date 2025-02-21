import threading
from constants import BUFFER_SIZE
from proximity.typing import MeanApproximator
from proximity.usonic import USonic
import rpigpioemul as GPIO
import math
import time
from maneuver import calculateManuever
import wheels
from wheels.util import cmToTick, tickToCm
from state import broker
import json 
import sys

# from fspace.util import findGap

import numpy as np

front = USonic(2, 3)
left = USonic(6, 5)


MINIMUM_FREE_SPACE = 18  # value in cm
MINIMUM_GAP_WIDTH = 16  # value in cm
MINIMUM_GAP_DEPTH = 32  # value in cm
HTL = 1
LTH = 0

__buffer = []

def push(v):
    global __buffer
    __buffer.append(v)
    if len(__buffer) > BUFFER_SIZE:
        __buffer.pop(0)

        time.sleep(0.01)


def findTransitions(measurements):
    mean = np.mean([x[1] for x in measurements])
    binary = [0 if x[1] < mean else 1 for x in measurements]
    prv = None
    transitions = []
    i = -1
    for v in binary:
        i += 1
        if prv == None:
            prv = v
            continue
        if prv > v:
            transitions.append((i, measurements[i], HTL))
        elif prv < v:
            transitions.append((i - 1, measurements[i - 1], LTH))
        prv = v
    return transitions


def findGaps(measurements):
    transitions = findTransitions(measurements)
    gaps = []
    i = 0
    while i < len(transitions):
        startIndex, start, t = transitions[i]
        if t == LTH and i < len(transitions) - 1:
            # next transition is ofcourse a HTL
            endIndex, end, tend = transitions[i + 1]  # next measurment
            width = tickToCm(end[0] - start[0])
            depth = np.mean([x[1] for x in measurements[startIndex:endIndex]])
            gaps.append((start, end, width, depth))
        i += 1
    return gaps

def __monitor():
    global __buffer
    prev = -1
    print('US.__monitor started')
    prevWasNone = False
    current = wheels.ticks()
    measures = []
    while True:
        t = wheels.ticks()
        if t > current:
            avg = np.mean(measures)
            m = (current, avg, wheels.getState())
            push(m)
            current = t
        else:
            l = left.distance()
            if(l is None): 
                continue
            measures.append(l if l <= MINIMUM_GAP_DEPTH * 1.2 else MINIMUM_GAP_DEPTH * 1.2  )
            if len(measures) >= 50:
                measures.pop(0)
        time.sleep(0.01)


def __analyze():
    global __buffer
    print('US.__analyze started')
    prev = 'hussain'
    while True:
        gaps = findGaps(__buffer)
        if len(gaps) > 0: print('found', len(gaps), 'gaps')
        validGaps = [
            gap for gap in gaps if gap[2] > MINIMUM_GAP_WIDTH and gap[3] > MINIMUM_GAP_DEPTH
        ]
        if len(validGaps) > 0 and prev != validGaps[0]:
            for g in range(0, len(validGaps)):
                print(f"({g}) {validGaps[g]}")
            broker.set("parkingSlot",  json.dumps(validGaps[0]) )
            prev = validGaps[0]
        elif len(validGaps) == 0 and prev != None:
            broker.delete("parkingSlot")
            prev = None
        time.sleep(0.5)


def park():
    P_SPEED = 50
    gap = broker.get('parkingSlot')
    if gap is None :
        return
    gap = json.loads(gap)
    print("Found valid gap", gap)
    s, e, width, depth = gap
    prox = min(  s[1], e[1] )  # distance to the nearest wall
    # move to the wall
    print("distance to the nearest wall=", prox)
    print(e[0])
    mid = (e[0] + s[0]) / 2
    print(f"mid={mid} c={wheels.ticks()} ticks={mid} ({tickToCm(mid)}cm)")
    wheels.moveExact(-P_SPEED * 30, 0, tickToCm(wheels.ticks() - mid - 8))
    manuever = calculateManuever(prox)
    for movement in manuever:
        wheels.moveExact(movement.speed * P_SPEED, movement.steering, movement.displacement)



monitorThread = threading.Thread(target=__monitor)
monitorThread.daemon = True
monitorThread.start()


analysisThread = threading.Thread(target=__analyze)
analysisThread.daemon = True
analysisThread.start()