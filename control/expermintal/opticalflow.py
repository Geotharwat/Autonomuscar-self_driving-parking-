# This module was intented to calculate the position of the car in a 2D space using optical flow
# by detecting local features in frames using Scale-invariant feature transform algorithm
# then supply the output points to Gunnar Farneback to find the translation and speed of the car
# 
# Results: the approach results was inaccurate as it was affected by different lighting conditiions

import cv2
from .. import util
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
import streaming.app as streaming
import wheels.wheels as wheels
from ldv2 import ldv2
import time
from maneuver import distance, calculateManuever

from navigation.process import start as startNavigationProcess


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


cap = None

if not RPI:  # if not on a pi, show track bars
    print("Running on desktop")
    # cap = cv2.VideoCapture("./videos/real.mp4")
    cap = cv2.VideoCapture("./videos/video.h264")
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
    cv2.createTrackbar("Seek", "Video", -1, 10, setSeek)
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



OPTICAL_FLOW_P_CM = 6.58

lastPixelPosition = pixelPosition = [0, 0]
position = [0, 0]
pixelSpeed = 0
speed = 0
lastMeasureTime = time.time()
epsilon = 30
motor_power = 50
MEASURE_INTERVAL = 0.1

def translation(frame1, frame2):
    # Extract keypoints from the first frame using SIFT
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(frame1, None)
    # Calculate optical flow of keypoints from frame 1 to frame 2 using Lucas-Kanade
    lk_params = dict(
        winSize=(15, 15),
        maxLevel=2,
        criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03),
    )
    kp1 = np.float32(np.array([x.pt for x in kp1]))
    if len(kp1) == 0:
        return (0, 0)
    kp2, st, err = cv2.calcOpticalFlowPyrLK(frame1, frame2, kp1, None, **lk_params)

    # Filter out keypoints with poor optical flow quality using RANSAC
    good_kp1 = []
    good_kp2 = []
    for i, (kpt1, kpt2) in enumerate(zip(kp1, kp2)):
        if st[i] and err[i] < 10:
            good_kp1.append(kpt1)
            good_kp2.append(kpt2)

    # Calculate mean displacement vector of remaining keypoints
    if len(good_kp1) == 0:
        return (0, 0)
    mean_disp = sum([kp2 - kp1 for kp1, kp2 in zip(good_kp1, good_kp2)]) / len(good_kp1)

    # Optionally, visualize keypoints and optical flow on second frame
    if not RPI:
        for kp1, kp2 in zip(good_kp1, good_kp2):
            cv2.circle(frame2, tuple(map(int, kp2)), 2, (0, 255, 0), -1)
            cv2.line(frame2, tuple(map(int, kp1)), tuple(map(int, kp2)), (0, 255, 0), 1)
        cv2.imshow("Optical Flow", frame2)

    return mean_disp

def adjustMotorPower(desiredSpeed=10):
    global motor_power, speed
    delta = desiredSpeed - abs(speed)
    if abs(delta) > 0.1 * desiredSpeed:
        motor_power += delta / (desiredSpeed * 2) * epsilon
        motor_power = (
            100 if motor_power > 100 else 0 if motor_power < 0 else motor_power
        )


def calculateSpeed():
    global lastPixelPosition, lastMeasureTime, pixelSpeed, speed
    if time.time() - lastMeasureTime < MEASURE_INTERVAL:
        return
    lastMeasureTime = time.time()
    pixelSpeed = distance(lastPixelPosition, pixelPosition) / MEASURE_INTERVAL
    speed = pixelSpeed / OPTICAL_FLOW_P_CM
    lastPixelPosition[0] = pixelPosition[0]
    lastPixelPosition[1] = pixelPosition[1]

previousDeltaPosition = [0, 0]
extremes = [1000, -1000, 0, 1]

manuever = calculateManuever(10)
currentMovement = manuever.pop(0)
dist = 0
step = time.time()


if __name__ == "__main__":
    # startNavigationProcess();
    prevFrame = None
    while True:
        if not RPI:
            # if not on RPI then this is a looping video
            if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                prevFrame = None
            elif seek > -1:
                cap.set(cv2.CAP_PROP_POS_FRAMES, seek)

        success, img = cap.read()

        resized = cv2.resize(img, (FRAME_WIDTH, FRAME_HEIGHT))
        noiselessImage = cv2.GaussianBlur(resized, (5, 5), 0)
        wrappedImage = util.warpImg(
            resized.copy(), wrappingPoints, FRAME_WIDTH, FRAME_HEIGHT
        )
        mask, filterResult = getFiltered(wrappedImage, filterValues)
       
        if not RPI:
            # Show stages
            cv2.imshow("Original", resized)
            cv2.imshow("Wrapped", wrappedImage)
            cv2.imshow("Mask", mask)
            # grayscale = cv2.cvtColor(wrappedImage, cv2.COLOR_BGR2GRAY)

        grayscale = cv2.resize(wrappedImage, (FRAME_WIDTH // 4, FRAME_HEIGHT // 4))
        calculateSpeed()
        pref_speed = 1
        adjustMotorPower(pref_speed)
        # adjust speed ,, constant 1cm/s

        # move to the target
        sign = 1
        if speed * 1.5 > pref_speed:
            sign = 0.1

        if currentMovement is None:
            exit()
        if dist >= currentMovement.displacement:
            dist = 0
            if len(manuever) == 0:
                currentMovement = None
            else:
                currentMovement = manuever.pop(0)
        else:
            # print("target", currentMovement.displacement - dist)
            wheels.steer(currentMovement.steering)
            print(
                f"target speed={speed}  dist={dist} rem={currentMovement.displacement - dist}\t\t  \n"
            )
            wheels.drive(sign * currentMovement.speed * 30)
            if step > -1:
                deltaTime = time.time() - step
                dist += speed * deltaTime
            step = time.time()

        # if abs(delta_target) < 10:
        #     wheels.drive(0)
        #     motor_power = 0
        # elif delta_target > 0:
        #     wheels.drive(sign * motor_power)
        # else:
        #     wheels.drive(sign * -motor_power)

        if prevFrame is not None:
            # start = time.time_ns()
            d = translation(prevFrame, grayscale)
            # print(f'translation took {(time.time_ns() - start)/1000000}ms\n', end="\r")
            dd = distance(previousDeltaPosition, d)
            pixelPosition[0] += d[0] if dd > 0.03 else 0
            pixelPosition[1] += d[1] if dd > 0.03 else 0
            previousDeltaPosition[0] = d[0]
            previousDeltaPosition[1] = d[1]
            extremes[2] += dd
            extremes[3] += 1
            position[0] = pixelPosition[0] / OPTICAL_FLOW_P_CM
            position[1] = pixelPosition[1] / OPTICAL_FLOW_P_CM
            if dd < extremes[0]:
                extremes[0] = dd
            if dd > extremes[1]:
                extremes[1] = dd
            # print(
            #     # f"{position} {extremes[:2]} avgDD={extremes[2]/extremes[3]} {dd}",
            #     end="\r",
            # )
        else:
            pixelPosition = [0, 0]
        # print("totalDis", totalDis, motor_power, end="\r")
        prevFrame = grayscale

        cv2.waitKey(1)
