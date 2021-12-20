#-------------------------------------------------------------------------------
# Name:        virtualDragDrop
# Purpose:
#
# Author:      kwalker
#
# Created:     20/12/2021
# Copyright:   (c) kwalker 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import sys, os
import math
import cv2
import numpy as np
import keyboard

#import cvzone
sys.path.append(os.path.join(sys.path[0], 'external_library',
    'cvzone-master','cvzone'))
from HandTrackingModule import HandDetector
from Utils import cornerRect

###################hand parameter#########################
'''
hand1 = hands[0]
lmlist1 = hand1["lmList"] #list of 21 landmarks points
bbox1 = hand1["bbox"] #bounding box info, x,y,w,h
centorPoint1 = hand1["center"] #center of the hand cx,cy
handType1 = hand1["type"] #hand type left or right
'''
#########################################################

cap = cv2.VideoCapture(0)
#width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
width = 1920
height = 1080
cap.set(3, width)    #set width resolution
cap.set(4, height)    #set height resolution
detector = HandDetector(detectionCon=0.8)  #init, 0.8 more accurate
colorR = (125,0,255)
colorC = (255, 150 , 125)
#print(width,height)
#rectangle
cx, cy, w, h= 100, 100, 200, 200
#circle
rx, ry, r = 200, 100, 85


class DragRect():
    def __init__(self, posCenter, size=[200,200]):
        self.posCenter = posCenter
        self.size = size

    def update(self, cursor):
        cx, cy = self.posCenter
        w, h = self.size

        if cx-w//2 < cursor[0] < cx+w//2 and cy-h//2 < cursor[1] < cy+h//2:
            colorR = (0,255,0)
            self.posCenter = cursor
        else:
            colorR = (125,0,255)

class DragCircle():
    def __init__(self, posCenter, radius=85):
        self.posCenter = posCenter
        self.radius = radius

    def update(self, cursor):
        rx, ry = self.posCenter
        r = self.radius
        dist = math.sqrt((cursor[0]-rx)**2 + (cursor[1]-ry)**2)
        if dist < r:
            colorC = (0,255,0)
            self.posCenter = cursor
        else:
            colorC = (125,150,255)

rectList = []
for x in range(3):
    rectList.append(DragRect([x*250+150,x*150+150]))

circleList = []
for x in range(2):
    circleList.append(DragCircle([900, x*200+250]))


while True:
    success, img = cap.read()   #template for webcam
    img = cv2.flip(img, 1) #0:vertical flip, 1:horizontal flip
    if img is None:
        print("camera not found")
        break

#this get landmark of your hand, can find finger points
    hands, img = detector.findHands(img, flipType=False)   #detect hand
    #print(hands)
    if hands:
        hand1 = hands[0]
        lmlist1 = hand1["lmList"] #list of 21 landmarks points

        if len(hands) == 2:
            hand2 = hands[1]
            lmlist2 = hand2["lmList"]

            dist = math.sqrt((lmlist1[12][0]-lmlist1[8][0])**2
            +(lmlist1[12][1]-lmlist1[8][1])**2) #distance of two tips

            dist2 = math.sqrt((lmlist2[12][0]-lmlist2[8][0])**2
            +(lmlist2[12][1]-lmlist2[8][1])**2) #distance of two tips

            print("dist: "+str(dist), "dist2: "+str(dist2))

            if dist < 40 and dist2 < 40:
                cursor = lmlist1[8]
                cursor2 = lmlist2[8]
                for rect in rectList:
                    rect.update(cursor)
                    rect.update(cursor2)
                for cir in circleList:
                    cir.update(cursor)
                    cir.update(cursor2)

            elif dist2 < 40:
                cursor2 = lmlist2[8]
                for rect in rectList:
                    rect.update(cursor2)
                for cir in circleList:
                    cir.update(cursor2)

            elif dist < 40:
                cursor = lmlist1[8]
                for rect in rectList:
                    rect.update(cursor)
                for cir in circleList:
                    cir.update(cursor)

        else:
            #index 8 is x,y of index finger tip, 12 is middle finger tip
            dist = math.sqrt((lmlist1[12][0]-lmlist1[8][0])**2
                +(lmlist1[12][1]-lmlist1[8][1])**2) #distance of two tips

            if dist < 40:
                cursor = lmlist1[8]
                for rect in rectList:
                    rect.update(cursor)
                for cir in circleList:
                    cir.update(cursor)

        #l, info, img = detector.findDistance(lmlist1[8],lmlist1[12],img)
            print("dist: "+str(dist))

#draw solid rectangle

##    for rect in rectList:
##        cx, cy = rect.posCenter
##        w, h = rect.size
##        cv2.rectangle(img, (cx-w//2, cy-h//2), (cx+w//2, cy+h//2),
##            colorR, cv2.FILLED)
##        cornerRect(img,(cx-w//2, cy -h//2, w, h), 20, rt=0)


#draw transperent rectangle
    imgNew = np.zeros_like(img, np.uint8)
    for rect in rectList:
        cx, cy = rect.posCenter
        w, h = rect.size
        cv2.rectangle(imgNew, (cx-w//2, cy-h//2), (cx+w//2, cy+h//2),
            colorR, cv2.FILLED)
        cornerRect(imgNew,(cx-w//2, cy-h//2, w, h), 20, rt=0)
    for cir in circleList:
        rx, ry = cir.posCenter
        r = cir.radius
        cv2.circle(imgNew, (rx, ry), r, colorC, -1)

    out = img.copy()
    alpha = 0.5
    mask = imgNew.astype(bool)
    out[mask] = cv2.addWeighted(img, alpha, imgNew, 1 - alpha, 0)[mask]

##########################################
    cv2.imshow("Image", out)    #temple for webcam (transperent)
    #cv2.imshow("Image", img)    #temple for webcam (solid)
    cv2.waitKey(1)  #temple for webcam

    if keyboard.is_pressed('q'):
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        sys.exit()
        break
