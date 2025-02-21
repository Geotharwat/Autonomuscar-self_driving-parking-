import sys
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
)
import constants as C
import streaming.app as streaming
import threading
import wheels as wheels
from ldv2 import ldv2

wrappingValues = np.copy(INITIAL_WRAPPING)
filterValues = [0, 255, 0, 48, 0, 221]
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
    cap = cv2.VideoCapture("./videos/real.mp4")
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

    cv2.namedWindow("Video")
    cv2.resizeWindow("Video", 480, 40)
    cv2.createTrackbar("Seek", "Video", 1, 1000, setSeek)

from math import atan2


def getMeanColor(img, x, y, w, h):
    # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    # Alternatively, create a mask
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    mask[y : y + h, x : x + w] = 255
    # Compute the average color of the ROI
    mean_color = cv2.mean(img, mask=mask)
    return (mean_color[0] + mean_color[1] + mean_color[2]) / 3


def drawSubRects(img, size=128):
    half = np.int32(0.5 / 4 * size)
    full = np.int32(1/ 4 * size)
    # full = np.int32(1 / 4 * size)
    srs = []
    y = half
    acc = 0
    count = 0
    while y < size - half:
        x = half
        while x < size - half:
            m = getMeanColor(img, x, y, full, full)
            acc += m
            count += 1
            srs.append([m, (x, y), (x + full, y + full)])
            x += full
        y += full
    avg = acc / count;
    a = (0,255,0)
    b = (255, 0, 0)

    for sr in srs:
        cv2.rectangle(img, sr[1], sr[2], a if sr[0] < avg else b, 1)


def noshadow(img):
    rgb_planes = cv2.split(img)
    result_norm_planes = []
    for plane in rgb_planes:
        dilated_img = cv2.dilate(plane, np.ones((7, 7), np.uint8))
        bg_img = cv2.medianBlur(dilated_img, 21)
        diff_img = 255 - cv2.absdiff(plane, bg_img)
        norm_img = cv2.normalize(
            diff_img,
            None,
            alpha=0,
            beta=255,
            norm_type=cv2.NORM_MINMAX,
            dtype=cv2.CV_8UC1,
        )
        result_norm_planes.append(norm_img)
    result_norm = cv2.merge(result_norm_planes)
    return result_norm


def detect_rectangles(image, values):
    # Load image
    # Convert to grayscale
    copy = image.copy()
    # mask, filterResult = getFiltered(copy, filterValues)
    shadowless = noshadow(copy)
    mask, filterResult = getFiltered(shadowless, filterValues)
    gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    # Apply thresholding to binarize the image
    # Find contours in the image
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop over contours and find rectangular shapes
    rectangles = []
    for contour in contours:
        perimeter = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.1 * perimeter, True)
        if len(approx) == 4:
            if cv2.contourArea(contour) > 100:
                rectangles.append(approx)
                cv2.drawContours(copy, [approx], 0, (0, 255, 0), 2)
            else:
                cv2.drawContours(copy, [approx], 0, (255, 0, 0), 2)

    # Draw rectangles on the image
    for rectangle in rectangles:
        cv2.drawContours(copy, [rectangle], 0, (0, 255, 0), 2)
    results = []
    size = 128
    for rect in rectangles:
        pts1 = np.float32(rect)
        pts2 = np.float32([[0, 0], [0, size], [size, size], [size, 0]])
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        imgWarp = cv2.warpPerspective(img, matrix, (size, size), cv2.INTER_LINEAR)
        results.append(imgWarp)
    return copy, results
    # Show the resulting image


images = []
for i in range(1, 3):
    filename = f"images/rect-v ({str(i)}).jpg"
    img = cv2.imread(filename)
    images.append((filename, img))


while True:
    for i in range(0, len(images)):
        rects, wrapped = detect_rectangles(images[i][1], filterValues)
        for imi in range(0, len(wrapped)):
            m = wrapped[imi]
            drawSubRects(m)
            cv2.imshow(f"{images[i][0]} rect({str(imi)})", m)
        cv2.imshow(f"Rectangles {str(i)}", rects)
    cv2.waitKey(1)

    # cv2.imshow(images[i][0], images[i][1])


# Display image with detected squares

cv2.destroyAllWindows()
