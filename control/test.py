import cv2
import numpy as np

# Define the function for lane detection and steering angle calculation
def lane_detection(frame):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection
    edges = cv2.Canny(blur, 50, 150)

    # Define the region of interest
    height, width = frame.shape[:2]
    roi_vertices = [(0, height), (width//2, height//2), (width, height)]
    mask = np.zeros_like(edges)
    cv2.fillPoly(mask, np.array([roi_vertices], np.int32), 255)
    masked_edges = cv2.bitwise_and(edges, mask)

    # Apply Hough line transform to detect lines
    lines = cv2.HoughLinesP(masked_edges, rho=2, theta=np.pi/180, threshold=50, minLineLength=50, maxLineGap=100)

    # Calculate the slope and intercept of the detected lines
    left_lines = []
    right_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1
        if slope < 0:
            left_lines.append((slope, intercept))
        else:
            right_lines.append((slope, intercept))

    # Calculate the average slope and intercept of the left and right lines
    left_avg = np.average(left_lines, axis=0)
    right_avg = np.average(right_lines, axis=0)

    # Calculate the x-coordinate of the intersection point between the left and right lines
    x = (left_avg[1] - right_avg[1]) / (right_avg[0] - left_avg[0])

    # Calculate the steering angle based on the position of the intersection point
    center = width // 2
    angle = (x - center) / center

    # Draw the detected lines on the frame
    line_image = np.zeros_like(frame)
    if len(left_lines) > 0:
        cv2.line(line_image, (int((height - left_avg[1]) / left_avg[0]), height),
                 (int((height * 0.6 - left_avg[1]) / left_avg[0]), int(height * 0.6)), (0, 0, 255), 5)
    if len(right_lines) > 0:
        cv2.line(line_image, (int((height - right_avg[1]) / right_avg[0]), height),
                 (int((height * 0.6 - right_avg[1]) / right_avg[0]), int(height * 0.6)), (0, 0, 255), 5)

    # Combine the frame and the detected lines
    result = cv2.addWeighted(frame, 0.8, line_image, 1, 0)

    return result, angle

# Read the video file
# Process each frame of the video

if __name__ == '__main__':
    frameCounter = 0;
    detectionInitialValues=[105,136,69,203];
    filterInitialValues=[86,112,0,59,127,255];
    cap = cv2.VideoCapture('ved.mp4');
    while True:
        frameCounter += 1
        if cap.get(cv2.CAP_PROP_FRAME_COUNT) == frameCounter:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frameCounter = 0
        success,img=cap.read()

        img=cv2.resize(img,(480,240))
        result, weight = lane_detection(img);
        cv2.imshow('Original', img)
        cv2.imshow('W', result)
        # motor.move(0.20, -curveVal * sen, 0.05)
        cv2.waitKey(1)