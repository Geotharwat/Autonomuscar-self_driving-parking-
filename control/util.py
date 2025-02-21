import numpy as np
import cv2


def thresHolding(img):
    imgHsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    whiteLimitLower=np.array([0, 3,0])
    whiteLimitUp = np.array([179, 255, 248])
    maskWhite=cv2.inRange(imgHsv,whiteLimitLower,whiteLimitUp)
    return  maskWhite

def warpImg (img,points,w,h,inv=False):
    pts1 = np.float32(points)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    if inv:
        matrix = cv2.getPerspectiveTransform(pts2, pts1)
    else:
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, matrix, (w, h))
    return imgWarp

def calculateWrappingPoints(values, wT=480, hT=270):
    widthTop,heightTop,widthBottom, heightBottom= values;
    points = np.int32([(widthTop, heightTop), (wT-widthTop, heightTop),
                      (widthBottom , heightBottom ), (wT-widthBottom, heightBottom)])
    return points



def nothing(a):
    pass

def initializeLaneThresholdsTrackbars(values):
    cv2.namedWindow("LaneThresholds")
    cv2.resizeWindow("LaneThresholds", 640, 300)
    cv2.createTrackbar("t1", "LaneThresholds", values[0], 200, nothing)
    cv2.createTrackbar("t2", "LaneThresholds", values[1], 200, nothing)
    cv2.createTrackbar("apertureSize", "LaneThresholds", values[2], 6, nothing)
    cv2.createTrackbar("rho", "LaneThresholds", values[3], 3, nothing)
    cv2.createTrackbar("theta", "LaneThresholds", values[4], 360, nothing)
    cv2.createTrackbar("minLineLength", "LaneThresholds", values[5], 300, nothing)
    cv2.createTrackbar("maxLineGap", "LaneThresholds", values[6], 150, nothing)
   

def initializeFiltrationTrackbars(values):
    cv2.namedWindow("Filter")
    cv2.resizeWindow("Filter", 640, 240)
    cv2.createTrackbar("HUE Min", "Filter", values[0], 179, nothing)
    cv2.createTrackbar("HUE Max", "Filter", values[1], 179, nothing)
    cv2.createTrackbar("SAT Min", "Filter", values[2], 255, nothing)
    cv2.createTrackbar("SAT Max", "Filter", values[3], 255, nothing)
    cv2.createTrackbar("VALUE Min", "Filter", values[4], 255, nothing)
    cv2.createTrackbar("VALUE Max", "Filter", values[5], 255, nothing)



def initializeDetectionTrackbars(intialTracbarVals,wT=480, hT=270):
    cv2.namedWindow("Detection")
    cv2.resizeWindow("Detection", 640, 360)
    cv2.createTrackbar("Width Top", "Detection", intialTracbarVals[0],wT//2, nothing)
    cv2.createTrackbar("Height Top", "Detection", intialTracbarVals[1], hT, nothing)
    cv2.createTrackbar("Width Bottom", "Detection", intialTracbarVals[2],wT//2, nothing)
    cv2.createTrackbar("Height Bottom", "Detection", intialTracbarVals[3], hT, nothing)

def valTrackbars(wT=480, hT=270):
    widthTop = cv2.getTrackbarPos("Width Top", "Detection")
    heightTop = cv2.getTrackbarPos("Height Top", "Detection")
    widthBottom = cv2.getTrackbarPos("Width Bottom", "Detection")
    heightBottom = cv2.getTrackbarPos("Height Bottom", "Detection")
    points = np.float32([(widthTop, heightTop), (wT-widthTop, heightTop),
                      (widthBottom , heightBottom ), (wT-widthBottom, heightBottom)])
    return points


def drawPoints(img,points):
    for x in range( 0,4):
        cv2.circle(img,(int(points[x][0]),int(points[x][1])),15,(0,0,255),cv2.FILLED)
    return img


def getHistogram(img, display=False, minPer=0.1, region=4):

    if region ==1:
        histValues = np.sum(img, axis=0)
    else:
        histValues=np.sum(img[img.shape[0]//region:,:],axis=0)


    maxValue = np.max(histValues)  # FIND THE MAX VALUE
    minValue = minPer * maxValue
    indexArray = np.where(histValues >= minValue)  # ALL INDICES WITH MIN VALUE OR ABOVE
    basePoint = int(np.average(indexArray))  # AVERAGE ALL MAX INDICES VALUES

    if display:

        imgHist = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)

        x=0
        for x,intensity in enumerate(histValues):
            val=(intensity[0]+intensity[1]+intensity[2] )//3
            if intensity[0]>minValue: color = (255, 0, 255)
            else: color = (0, 0, 255)
            # cv2.line(imgHist, (x, img.shape[0]), (x,img.shape[0] - val// 255 // region ), color, 1)

        # cv2.circle(imgHist,(basePoint,img.shape[0]),20,(0,255,255),cv2.FILLED)
        return  basePoint,imgHist
    return basePoint

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver