
import cv2
import numpy as np
from constants import RPI, FRAME_WIDTH, FRAME_HEIGHT


def get_average_line_angle(frame):
    """
    Computes the average angle of lines in a pre-processed image using OpenCV.

    Args:
        frame: A pre-processed frame.

    Returns:
        The signed average angle from the y-axis.
    """

    # Detect lines using HoughLinesP
    lines = cv2.HoughLinesP(frame, 1, np.pi/180, 100, minLineLength=130, maxLineGap=10)

    # Compute angles of line segments
    angles = []
    if lines is None :return 90
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2-y1, x2-x1)
        angles.append(angle)

    # Compute average angle
    sin_avg = np.mean(np.sin(angles))
    cos_avg = np.mean(np.cos(angles))
    avg_angle = np.arctan2(sin_avg, cos_avg)

    # Convert angle to degrees and sign it from the y-axis
    avg_angle = np.rad2deg(avg_angle)
    signed_angle = -avg_angle if avg_angle < 0 else 180 - avg_angle

    return signed_angle


def ldv2(frame, values):
    # Define the parameters for the lane detection algorithm
    # threshold1 = 50  
    # threshold2 = 150
    # apertureSize = 3
    # rho = 1
    # theta = np.pi / 180
    # minLineLength = 100
    # maxLineGap = 50
    if not RPI:
        frame = frame.copy()
    apertureSize = 3
    rho = 3
    threshold1 = values[0]
    threshold2 = values[1]
    theta = np.pi / max(1, values[2])
    minLineLength = values[3]
    maxLineGap = values[4]

    # Apply Canny edge detection
    edges = cv2.Canny(frame, threshold1, threshold2, apertureSize=apertureSize)
    # Apply Hough line detection
    lines = cv2.HoughLinesP(edges, rho, theta, minLineLength, maxLineGap)
    print(lines)

    # Draw the detected lines on the frame
    if lines is not None:
        if not RPI:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Calculate the steering angle
        steering_angle = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            steering_angle += np.arctan2(y1 - y2, x1 - x2)

        steering_angle = steering_angle / len(lines)
        print('delta=%d', steering_angle, steering_angle/np.pi * 180)
        x1 = 0
        y1 = int((x1 - FRAME_WIDTH/2) * np.tan(steering_angle) + FRAME_HEIGHT/2)
        x2 = FRAME_WIDTH - 1
        y2 = int((x2 - FRAME_WIDTH/2) * np.tan(steering_angle) + FRAME_HEIGHT/2)

        # draw the line on the image
        thickness = 10
        color = (0, 0, 255)
        if not RPI:
            cv2.line(frame, (x1, y1), (x2, y2), color, thickness)
      
    else:
        steering_angle = 0
    return frame,  steering_angle/np.pi * 180


