import sys
import threading
from Detection import lanCurve
import cv2
import util
from ColorPicker import getFiltered
import numpy as np
from constants import (
    RPI,
    INITIAL_WRAPPING,
    INITIAL_DETECTION,
    INITIAL_FILTER,
    FRAME_WIDTH,
    FRAME_HEIGHT,
    MODE_SELF_DRIVING,
    MODE_SELF_PARKING,
    MODE_IDLE,
    MODE_CONTROL
)
import constants as C
import wheels
from ldv2 import get_average_line_angle
import time
import math
from maneuver import calculateManuever, distance
from us import park
from state import getMode, broker , getControls

wrappingValues = np.copy(INITIAL_WRAPPING)
filterValues = np.copy(INITIAL_FILTER)
detectionValues = np.copy(INITIAL_DETECTION)
wrappingPoints = util.calculateWrappingPoints(wrappingValues)
seek = -1


def setFilterValue(index, value):
    filterValues[index] = value


def setWrappingValue(index, value):
    global wrappingPoints
    wrappingValues[index] = value
    wrappingPoints = util.calculateWrappingPoints(wrappingValues)


def setDetectionValue(index, value):
    global detectionValues
    detectionValues[index] = value


def setSeek(value):
    global seek
    seek = value


cap =  cv2.VideoCapture("/dev/video0", cv2.CAP_V4L) if RPI else cv2.VideoCapture("videos/calibration.mp4")

if not cap.isOpened():
    broker.publish('error', 'Cannot open camera!')
    print("Cannot open camera")
    exit()

if not RPI:  # if not on a pi, show track bars
    print("Running on desktop")
    
    # cap = cv2.VideoCapture("./videos/video.h264")
    cv2.namedWindow("Filter")
    cv2.createTrackbar(
        "HUE Min", "Filter", filterValues[0], 255, lambda v: setFilterValue(0, v)
    )
    cv2.createTrackbar(
        "HUE Max", "Filter", filterValues[1], 255, lambda v: setFilterValue(1, v)
    )
    cv2.createTrackbar(
        "SAT Min", "Filter", filterValues[2], 255, lambda v: setFilterValue(2, v)
    )
    cv2.createTrackbar(
        "SAT Max", "Filter", filterValues[3], 255, lambda v: setFilterValue(3, v)
    )
    cv2.createTrackbar(
        "VALUE Min", "Filter", filterValues[4], 255, lambda v: setFilterValue(4, v)
    )
    cv2.createTrackbar(
        "VALUE Max", "Filter", filterValues[5], 255, lambda v: setFilterValue(5, v)
    )

    cv2.namedWindow("Wrapping")
    cv2.resizeWindow("Wrapping", 480, 160)
    cv2.createTrackbar(
        "Width Top",
        "Wrapping",
        wrappingValues[0],
        FRAME_WIDTH // 2,
        lambda v: setWrappingValue(0, v),
    )
    cv2.createTrackbar(
        "Height Top",
        "Wrapping",
        wrappingValues[1],
        FRAME_HEIGHT,
        lambda v: setWrappingValue(1, v),
    )
    cv2.createTrackbar(
        "Width Bottom",
        "Wrapping",
        wrappingValues[2],
        FRAME_WIDTH // 2,
        lambda v: setWrappingValue(2, v),
    )
    cv2.createTrackbar(
        "Height Bottom",
        "Wrapping",
        wrappingValues[3],
        FRAME_HEIGHT,
        lambda v: setWrappingValue(3, v),
    )

    cv2.namedWindow("Video")
    cv2.resizeWindow("Video", 480, 40)
    cv2.createTrackbar("Seek", "Video", -1, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)), setSeek)
    if C.ALG == C.Algorithm.LDV2:
        # New lane detection
        cv2.namedWindow("LDV2 Parameters", cv2.WINDOW_AUTOSIZE)
        cv2.createTrackbar(
            "threshold1",
            "LDV2 Parameters",
            detectionValues[0],
            255,
            lambda v: setDetectionValue(0, v),
        )
        cv2.createTrackbar(
            "threshold2",
            "LDV2 Parameters",
            detectionValues[1],
            255,
            lambda v: setDetectionValue(1, v),
        )
        cv2.createTrackbar(
            "theta",
            "LDV2 Parameters",
            detectionValues[2],
            360,
            lambda v: setDetectionValue(2, v),
        )
        cv2.createTrackbar(
            "minLineLength",
            "LDV2 Parameters",
            detectionValues[3],
            255,
            lambda v: setDetectionValue(3, v),
        )
        cv2.createTrackbar(
            "maxLineGap",
            "LDV2 Parameters",
            detectionValues[4],
            255,
            lambda v: setDetectionValue(4, v),
        )

else:
    print("Running on pi")


def drawAreaOfInterest(img):
    pts = np.array(
        [wrappingPoints[0], wrappingPoints[1], wrappingPoints[3], wrappingPoints[2]],
        np.int32,
    )
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, (0, 0, 255))


previousDeltaPosition = [0, 0]
extremes = [1000, -1000, 0, 1]

manuever = calculateManuever(10)
currentMovement = manuever.pop(0)
dist = 0
step = time.time()


__benchmark_time = 0


def benchmark_start():
    global __benchmark_time
    __benchmark_time = time.time_ns() // 1000

def benchmark_end(name):
    global __benchmark_time
    t = time.time_ns() // 1000
    print(f'{name} {t - __benchmark_time}us');

angle = 90
__angles = []
def measureAngle():
    global __angles, angle
    while True:
        if not RPI:
            # if not on RPI then this is a looping video
            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            elif seek > -1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, seek)
        success, img = cap.read()
        if(success == False):
            print('cap.read failed!')
            time.sleep(1)
            return
        resized = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))
        noiselessImage = cv2.GaussianBlur(resized, (5, 5), 0)
        wrappedImage = util.warpImg(
            noiselessImage.copy(), wrappingPoints, FRAME_WIDTH, FRAME_HEIGHT
        )
        mask, filterResult = getFiltered(wrappedImage, filterValues)
        direction = 0
        gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        __angles.append(get_average_line_angle(gray))
        if len(__angles) > 5:
            __angles.pop(0)
        angle = np.mean(__angles)
        # print('angle=', angle)
        invWRap = util.warpImg(
            mask, wrappingPoints, FRAME_WIDTH, FRAME_HEIGHT, True
        )
        gizmosImage = resized.copy()
        gizmosImage = cv2.add(gizmosImage, invWRap)
        drawAreaOfInterest(gizmosImage)
        cx, cy = np.int32(np.divide(np.sum(wrappingPoints, axis=0), len(wrappingPoints)))
        if direction == 0:
            # arrow forward
            cv2.arrowedLine(
                gizmosImage, (cx, cy + 40), (cx, cy - 40), (255, 0, 100), 3, 8, 0, 0.1
            )
        elif direction < 0:
            # arrow left
            cv2.arrowedLine(
                gizmosImage, (cx + 40, cy), (cx - 40, cy), (255, 0, 100), 3, 8, 0, 0.1
            )
        else:
            cv2.arrowedLine(
                gizmosImage, (cx - 40, cy), (cx + 40, cy), (255, 0, 100), 3, 8, 0, 0.1
            )
            # arrow right
        ret, buffer = cv2.imencode(".jpg", gizmosImage)
        broker.publish('video_feed_original', buffer.tobytes())
        if not RPI:
            cv2.imshow("original", noiselessImage)
            cv2.imshow("mask", mask)
            cv2.imshow("Gizmos", gizmosImage)
        cv2.waitKey(1)


def selfDriving():
    global angle
    if C.ALG == C.Algorithm.LDV2:
        direction = 0
        if angle > 150 and angle > 110 :
            wheels.moveExact(-10, 0, 10)
        if angle < 40 and angle < 80 :
            wheels.moveExact(-10, 0, 10)
        if angle < 110 and angle > 80:
            direction = 0
        elif angle > 100:
            direction = -1
        else:
            direction = 1
        wheels.drive(10)
        wheels.steer(direction)
    else:
        steer = lanCurve(mask)
        if steer < -0.005:
            direction = -1
        elif steer > 0.005:
            direction = 1
        else:
            direction = 0

stateReportingThread = threading.Thread(target=measureAngle)
stateReportingThread.daemon = True
stateReportingThread.start()

if __name__ == "__main__":
    # ----- start the server ------
    # startNavigationProcess();
    # if C.ENABLE_SERVER:
    #     # start streaming thread
    #     stateReportingThread = threading.Thread(target=streaming.listen)
    #     stateReportingThread.daemon = True
    #     stateReportingThread.start()
    prevFrame = None
    while True:
        if getMode() ==  MODE_SELF_DRIVING:
            # wheels.drive(15)
            selfDriving()
        elif getMode() ==  MODE_SELF_PARKING:
            park()
            broker.set('mode', MODE_IDLE)
        elif getMode() == MODE_CONTROL:
            x, y = getControls()
            wheels.steer(x)
            wheels.drive(y * 0.25)
        else:
            wheels.drive(0)
            wheels.steer(0)
            time.sleep(0.1)
