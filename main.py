import cv2
import thread
import math
import time
import numpy as np
from object import Object
from cvHelper import *
#from adaHelper import *



# === Button ===
#from periphery import GPIO
#enable_switch = GPIO(160, "in")


steeringDullness = 75 #set between 1 and 100. eg: 30 means line/object must move across 30% of the image width to get 100% steering output
                            #2018 tweak this, since we're polling the camera much faster.    

#cap = cv2.VideoCapture(0)    
#while(cap.isOpened()):    
while(1):
    # ON Button code
    # while(not enable_switch.read()):
    #     # We want to pause the program        
    #     time.sleep(1)

    #_,frame = cap.read()
    frame=cv2.imread('straightdummy.png')
    frame = resizeMe(frame,3)
    height, width = int(frame.shape[0]), int(frame.shape[1])

    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    #Threshholds for colour
    maskblue, pixels_blue     = colourMaskMe(frame,"blue")    
    maskpurple, pixels_purple = colourMaskMe(frame,"purple")
    maskyellow, pixels_yellow = colourMaskMe(frame,"yellow")
    maskgreen, pixels_green   = colourMaskMe(frame,"green")
    maskred, pixels_red       = colourMaskMe(frame,"red")


    blueLine   = Object(*centroidAndBoundsFinder(pixels_blue, maskblue, 0))
    yellowLine = Object(*centroidAndBoundsFinder(pixels_yellow, maskyellow, 0))
    obs        = Object(*centroidAndBoundsFinder(pixels_red, maskred, 0))

    drawBlueLineContours(frame, pixels_blue, maskblue, 0)
    drawYellowLineContours(frame, pixels_yellow, maskyellow, 0)
    drawRedObjectContours(frame, pixels_red, maskred, 0)


    #NEED TO ADD GREEN FOR FINISHLINE!!!

    #TODO: write height and width in comment

    #obstacle avoidance and vector correction 
    if obs.leftX > yellowLine.centerY and obs.rightX < blueLine.centerY:            #2018  if the object is between the left and right lines (yellow, blue)
        if (obs.leftX - yellowLine.centerY) < (blueLine.centerY - obs.rightX):        #2018 decide which way around obstacle to go , around left or right..? what about equal?
            leftCol = obs.rightX                #2018 LOA and ROA?
            rightCol = blueLine.centerX             #what if there are a bunch of objects on the road?
        else:
            leftCol = yellowLine.centerX
            rightCol = obs.leftX
    else:
        leftCol = yellowLine.centerX
        rightCol = blueLine.centerX

    #steering dullness/sharpness
    leftCol = leftCol
    if leftCol > width:
        leftCol = width

    rightCol = width - (width - rightCol)
    if rightCol < 0:
        rightCol = 0

    steerSpot = (((leftCol+rightCol)/2), int(height/1.1))
    leftTop = (leftCol, 0)
    leftBot = (leftCol, height)

    rightTop = (rightCol, 0 )
    rightBot = (rightCol, height)



    #steer_pulse = map_pulse(angle, 40, 132, steer_min, steer_max)
    #pwm.set_pwm(steer, 0, steer_pulse)
    #print(str(steer_pulse))
    

    res = cv2.bitwise_and(frame,frame, mask=maskyellow+maskblue+maskred)
    red = cv2.bitwise_and(frame,frame, mask=maskred)
    blu = cv2.bitwise_and(frame,frame, mask=maskblue)
    pur = cv2.bitwise_and(frame,frame, mask=maskpurple)
    yel = cv2.bitwise_and(frame,frame, mask=maskyellow)
    grn = cv2.bitwise_and(frame,frame, mask=maskgreen)
    botMid = (width/2, height)
    cv2.arrowedLine(res, botMid, steerSpot, (255,255,255), 3)

    cv2.line(res, leftTop, leftBot, (0,255,255), 1)
    cv2.line(res, rightTop, rightBot, (255,0,0), 1)
    

#    cv2.imshow("blue", blu)
#    cv2.imshow("purple", pur)
#    cv2.imshow("yellow", yel)
#    cv2.imshow("red", red)
#    cv2.imshow("green", grn)
    cv2.imshow("all", res)

#    time.sleep(0.3); print "Time delay operating"
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release
cv2.destroyAllWindows