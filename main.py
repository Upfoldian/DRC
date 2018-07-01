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


# # === MOVEMENT STUFF ===
# import Adafruit_PCA9685

# def map_pulse(val, inMin, inMax, outMin, outMax):
#     return int((val - inMin) * (outMax - outMin) / (inMax - inMin) + outMin);

# pwm = Adafruit_PCA9685.PCA9685()
# freq = 100
# pwm.set_pwm_freq(freq)
# #Channels
# steer     = 0
# gas       = 2
# relay     = 3
# # Steering
# steer_mid = 600
# steer_max = 800
# steer_min = 400
# # Gas
# gas_min = 400 #450
# gas_max = 800 #850


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
    height, width = frame.shape[0], frame.shape[1]

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
            left_of_arc = obs.rightX                #2018 LOA and ROA?
            right_of_arc = blueLine.centerX             #what if there are a bunch of objects on the road?
        else:
            left_of_arc = yellowLine.centerX
            right_of_arc = obs.leftX
    else:
        left_of_arc = yellowLine.centerX
        right_of_arc = blueLine.centerX

    #steering dullness/sharpness
    left_of_arc = left_of_arc * 100 / steeringDullness
    if left_of_arc > width:
        left_of_arc = width

    right_of_arc = width - (width - right_of_arc) * 100 / steeringDullness
    if right_of_arc < 0:
        right_of_arc = 0

    angle = ((left_of_arc+right_of_arc)/2) * 100 / width
    angle = 100 - angle

    #steer_pulse = map_pulse(angle, 40, 132, steer_min, steer_max)
    #pwm.set_pwm(steer, 0, steer_pulse)
    #print(str(steer_pulse))
    

    res = cv2.bitwise_and(frame,frame, mask=maskyellow+maskblue+maskred)
    red = cv2.bitwise_and(frame,frame, mask=maskred)
    blu = cv2.bitwise_and(frame,frame, mask=maskblue)
    pur = cv2.bitwise_and(frame,frame, mask=maskpurple)
    yel = cv2.bitwise_and(frame,frame, mask=maskyellow)
    grn = cv2.bitwise_and(frame,frame, mask=maskgreen)

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