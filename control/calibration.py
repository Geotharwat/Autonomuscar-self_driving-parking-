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
)
import constants as C
from ldv2 import get_average_line_angle
import time
import math

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



def drawAreaOfInterest(img):
    pts = np.array(
        [wrappingPoints[0], wrappingPoints[1], wrappingPoints[3], wrappingPoints[2]],
        np.int32,
    )
    pts = pts.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, (0, 0, 255))

if __name__ == "__main__":
   
    frame = 0
    while True:
       if not RPI:
        # if not on RPI then this is a looping video
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frame = 0
        elif seek > -1:
            cap.set(cv2.CAP_PROP_POS_FRAMES, seek)
        success, img = cap.read()
        if(success == False):
            print('cap.read failed!')
            time.sleep(1)
            continue
        resized = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))
        noiselessImage = cv2.GaussianBlur(resized, (5, 5), 0)
        wrappedImage = util.warpImg(
            resized.copy(), wrappingPoints, FRAME_WIDTH, FRAME_HEIGHT
        )
        mask, filterResult = getFiltered(wrappedImage, filterValues)
        steer = 0
        # ---- draw gizmos -----
        invWRap = util.warpImg(
            mask, wrappingPoints, FRAME_WIDTH, FRAME_HEIGHT, True
        )
        gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
        angle = get_average_line_angle(gray)
        print('angle=', angle)

        gizmosImage = resized.copy()
        gizmosImage = cv2.add(gizmosImage, invWRap)
        drawAreaOfInterest(gizmosImage)
        aoiPoints = tuple(map(tuple, wrappingPoints))
        cx, cy = np.int32(np.divide(np.sum(wrappingPoints, axis=0), len(wrappingPoints)))
        direction = 0
        if angle < 100 and angle > 80:
            # arrow forward
            cv2.arrowedLine(
                gizmosImage, (cx, cy + 40), (cx, cy - 40), (255, 0, 100), 3, 8, 0, 0.1
            )
            direction = -1
        elif angle > 100:
            # arrow left
            cv2.arrowedLine(
                gizmosImage, (cx + 40, cy), (cx - 40, cy), (255, 0, 100), 3, 8, 0, 0.1
            )
            direction = 1
        else:
            cv2.arrowedLine(
                gizmosImage, (cx - 40, cy), (cx + 40, cy), (255, 0, 100), 3, 8, 0, 0.1
            )
            direction = 0
        # arrow right
        cv2.imshow("Gizmos", gizmosImage)
        cv2.imshow("Mask", mask)
        
        cv2.waitKey(1)
