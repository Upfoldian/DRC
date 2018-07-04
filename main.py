import cv2
import thread
import math
import time
import numpy as np
from object import Object
from cvHelper import *
from adaHelper import *



# === Button ===
from periphery import GPIO
enable_switch = GPIO(160, "in")

# === DEBUG ===  
flag = False
count = 1

cap = cv2.VideoCapture(0)    
# === 
pastAngles = [0,0] # used to smooth out
startUp = True
velo = 700 #between 600 and 800 for forwards

while(cap.isOpened()):    
    # ON Button code
    while(not enable_switch.read()):
        # We want to pause the program    
	pwm.set_pwm(steer, 0, steer_mid)
	pwm.set_pwm(gas, 0, gas_mid)    
        time.sleep(1)
	startUp = False

    # Image Capture
    _,frame = cap.read()
    #frame=cv2.imread('obsflipdummy.png')

    saveFrame = frame
    
    frame = resizeMe(frame,3)
    #frame = frame[frame.shape[0]/2:frame.shape[0]-1,:,:]
    #frame=np.uint8((frame.astype(float)/16.)**2)
    #frame = chromatifyMe(frame)
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

    #Adds debug dots onto final image for centroids
    drawBlueLineContours(frame, pixels_blue, maskblue, 0)
    drawYellowLineContours(frame, pixels_yellow, maskyellow, 0)
    drawRedObjectContours(frame, pixels_red, maskred, 0)

    # Adjusts line location based on size of bounding box for better steering
    yellowLine.centerX = yellowLine.leftX + (yellowLine.centerX-yellowLine.leftX)/2 
    blueLine.centerX = blueLine.centerX +  (blueLine.rightX-blueLine.centerX)/2


    if (flag == False):
        print "W: ", width, "H: ", height
        print "YX: ", yellowLine.centerX, "YY: ", yellowLine.centerY
        print "LeftX: ", obs.leftX, "YCent: ", yellowLine.centerX, " | RightX: ", obs.rightX, " BCent: ", blueLine.centerX
        flag = True
    #Edge placement code (blue on left, yellow on right)
    if obs.leftX < yellowLine.centerX and obs.rightX > blueLine.centerX: 
        if (yellowLine.centerX - obs.rightX) > (obs.leftX - blueLine.centerX): 
            rightCol = yellowLine.centerX               #2018 LOA and ROA?
            leftCol =  obs.rightX             #what if there are a bunch of objects on the road?
        else:
            rightCol = obs.leftX
            leftCol = blueLine.centerX
    else:
        rightCol = yellowLine.centerX
        leftCol = blueLine.centerX

    #Fixing bounds
    if leftCol < 0:
        leftCol = 0
    if rightCol > width:
        rightCol = width

    #Very basic error correction
    if rightCol <= leftCol:
	rightCol = width
    if leftCol >= rightCol:
	leftCol = 0

    #So we can see the drawn lines
    if (yellowLine.centerX == width):
	yellowLine = Object(width-4, width-4, width-4, height/2)
    if (blueLine.centerX == 0):
	blueLine = Object(4,4,4, height/2)

    steerSpot = (((leftCol+rightCol)/2), int(height/2))
    leftTop = (leftCol, 0)
    leftBot = (leftCol, height)

    rightTop = (rightCol, 0 )
    rightBot = (rightCol, height)

    #Image Masking
    res = cv2.bitwise_and(frame,frame, mask=maskyellow+maskblue+maskred+maskgreen)
    red = cv2.bitwise_and(frame,frame, mask=maskred)
    blu = cv2.bitwise_and(frame,frame, mask=maskblue)
    pur = cv2.bitwise_and(frame,frame, mask=maskpurple)
    yel = cv2.bitwise_and(frame,frame, mask=maskyellow)

    # Finish Line / Green line
    grn = cv2.bitwise_and(frame,frame, mask=maskgreen)
    grncrop = grn[int(grn.shape[0]/1.05):grn.shape[0]-1,:,:]
  
    total = grncrop.size * 1.0
    green_count = np.count_nonzero(grncrop)

    #if (green_count/total) > 0.25:
	#while(True):
	    #time.sleep(1)
	    #pwm.set_pwm(steer, 0, steer_mid)
	    #pwm.set_pwm(gas, 0, gas_mid) 

    # Draws some helper lines
    botMid = (width/2, height)
    
    cv2.line(res, leftTop, leftBot, (255,0,0), 1)
    cv2.line(res, rightTop, rightBot, (0,255,255), 1)
    
    o = height - steerSpot[1]
    a = float(abs(steerSpot[0] - botMid[0]))
    #Steering and steering line calculations
    if (a != 0):
        angle = np.arctan(o / a)
        angle = 90 - np.rad2deg(angle)
    else: 
        angle = 0
    if (steerSpot[0] - botMid[0] < 0):
	   angle = angle * -1

    if (angle > 25):
	   angle = 25
    elif (angle < -25):
	   angle = -25
    

    #Tries to smooth out steering by taking average of last 5 frames
    for i in range(len(pastAngles)-1):
        pastAngles[-2-i+1] = pastAngles[-2-i]
    pastAngles[0] = angle
    avg = sum(pastAngles)/5.0

    o = height/2.0 * np.tan(np.deg2rad(avg))
    avgPoint = (int(botMid[0] + o), int(height/2))

    cv2.arrowedLine(res, botMid, steerSpot, (255,255,255), 3)
    cv2.arrowedLine(res, botMid, avgPoint, (0, 255, 0), 3)

    #Car motion commands
    steer_pulse = map_pulse(avg, -25, 25, steer_min, steer_max)
    pwm.set_pwm(steer, 0, steer_pulse)
    if (startUp == True):
	pwm.set_pwm(gas, 0, gas_max)
    else:
        pwm.set_pwm(gas, 0, velo)
    print "Angle: ", int(angle), " Steer: ", steer_pulse, " Velo: ", velo

#    cv2.imshow("blue", blu)
#    cv2.imshow("purple", pur)
#    cv2.imshow("yellow", yel)
#    cv2.imshow("red", red)
#    cv2.imshow("green", grncrop)
#    cv2.imshow("original", saveFrame)
#    cv2.imshow("all", res)

#    filename = "./img/test/" + str(count) + ".png"
#    cv2.imwrite(filename, frame)
#    time.sleep(0.3); #print "Time delay operating"

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release
cv2.destroyAllWindows
