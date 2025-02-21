import cv2
import numpy as np
import util

curveList=[]
avgVal=10

def lanCurve(img):
    midPoint, imgHist = util.getHistogram(img, display=True, minPer=0.5, region=4)
    curveAveragePoint,imgHist=util.getHistogram(img,display=True,minPer=0.9)
    curveRaw=curveAveragePoint-midPoint
    curveList.append(curveRaw)
    if len(curveList) > avgVal:
        curveList.pop(0)
    curve=int(sum(curveList)/len(curveList))
    curve=curve/100
    if curve>1: curve==1
    if curve<-1:curve==-1
    return curve
