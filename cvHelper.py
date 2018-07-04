#helper.py
import cv2
import thread
import math
import time
import numpy as np
from object import Object

# === OpenCV ===
min_pixel_detect     = 100
blurksize            = 1 #5
dilateksize          = 5 #5

#Set up the various kernels - the blur, dilate and disparity (close holes) kernels
blurkernel         = np.ones((blurksize,blurksize),np.uint8)
dilatekernel     = np.ones((dilateksize,dilateksize),np.uint8)

def chromatifyMe(frame):
    retframe=frame.copy().astype(float)
    sumframe = np.sum(frame,2)
    sumframe = sumframe.reshape(sumframe.shape[0],sumframe.shape[1],1).repeat(3,2)
    retframe = np.round(np.divide(retframe, sumframe, out=np.zeros_like(retframe), where=sumframe!=0)*255.)
    return np.uint8(retframe)

def resizeMe(frame, scl):
    return cv2.resize(frame,(0,0),fx=1./scl,fy=1./scl)                #rescale it. 

def centroidAndBoundsFinder(pixel_count_colour, thresh_colour, cx_for_no_detection):
    # set defaults.
    cx = cx_for_no_detection
    lx = cx
    rx = cx
    cy = int(thresh_colour.shape[1]/2)

    if (pixel_count_colour > min_pixel_detect): 
        #Find contours
        #Note 2018 - is contours best approach? spline fitting perhaps faster/better for interpolating?
        contimageout, contours, hierarchy  = cv2.findContours(thresh_colour, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) > 0:
            #Find contour with max area
            max_area = 0 #initialize max area of contour
            best_contour = contours[0] #initialize the 'best' contour
            for thiscont in contours:
                M = cv2.moments(thiscont)
                area = M['m00']
                if area > max_area:
                    max_area = area
                    best_contour = thiscont

            if area != 0:
                #left and right edge finding
                lx, ty, cont_width, cont_height = cv2.boundingRect(best_contour) 
                #lx, ty, cont_width, cont_height = cv2.minAreaRect(best_contour) 
                rx = lx + cont_width

                #Centroid finding
                moments = cv2.moments(best_contour)
                cx, cy = int(moments['m10']/moments['m00']), int(moments['m01']/moments['m00']), 

    return cx, lx, rx, cy 

def colourMaskMe(frame,color):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if(color=="yellow"): # yellow for the left side
        lower = np.array([15,125,125])
        upper = np.array([40,255,255])

    if(color=="blue"): # blue for the right side
        lower = np.array([100,75,75])
        upper = np.array([125,255,255])

    if(color=="red"): #red for other cars
        lower= np.array([160,75,75])
        upper= np.array([255,255,255])

    if(color=="purple"): #purple for obstacles
        lower = np.array([130,75,75])
        upper = np.array([160,255,255])

    if(color=="green"): #green for finishline
        lower = np.array([40,50,50])
        upper = np.array([80,250,250])

    frame=cv2.inRange(hsv, lower, upper)

    if(color=="red"): #this is red also - forming a notch bandpass. Dont need to do it for other colours
        lower= np.array([0,150,150])
        upper= np.array([7,255,255])
        frame=frame+cv2.inRange(hsv, lower, upper)

    mask = cv2.dilate(frame,dilatekernel,iterations = 1)
    return mask, np.count_nonzero(mask)


def drawBlueLineContours(frame, pixels_blue, maskblue, cx_for_no_detection):
    blueLine = Object(*centroidAndBoundsFinder(pixels_blue, maskblue, cx_for_no_detection))
    cv2.circle(frame, (blueLine.centerX, blueLine.centerY), 5, (0,0,255), -1)

def drawYellowLineContours(frame, pixels_yellow, maskyellow, cx_for_no_detection):
    yellowLine = Object(*centroidAndBoundsFinder(pixels_yellow, maskyellow, cx_for_no_detection))
    cv2.circle(frame, (yellowLine.centerX,yellowLine.centerY), 5, (0,0,255), -1)

def drawRedObjectContours(frame, pixels_red, maskred, cx_for_no_detection):
    obs = Object(*centroidAndBoundsFinder(pixels_red, maskred, 0))
    cv2.circle(frame, (obs.leftX,obs.centerY), 5, (0,255,0), -1)
    cv2.circle(frame, (obs.rightX,obs.centerY), 5, (255,0,0), -1)
