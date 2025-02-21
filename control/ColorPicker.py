import cv2
import numpy as np
import util




def getFiltered(img, values):
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h_min = values[0];
    h_max = values[1];
    s_min = values[2];
    s_max = values[3];
    v_min = values[4];
    v_max = values[5];

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(imgHsv, lower, upper)
    result = cv2.bitwise_and(img, img, mask=mask)

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    return [mask, result];


if __name__ == '__main__':
    frameCounter = 0
    cap = cv2.VideoCapture('real.mp4')
    filterInitialValues=[86,112,0,59,127,255];
    util.initializeFiltrationTrackbars(filterInitialValues);

    while True:
        frameCounter += 1
        if cap.get(cv2.CAP_PROP_FRAME_COUNT) == frameCounter:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            frameCounter = 0
        _, img = cap.read()
        cv2.resize(img,(480,240))
        cv2.imshow('Horizontal Stacking', getFiltered(img))
        if cv2.waitKey(1) and 0xFF == ord('q'):
            break

# cap.release()
# cv2.destroyAllWindows()