from __future__ import division
import time

# Import the PCA9685 module.
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()

def map_pulse(val, inMin, inMax, outMin, outMax):
    return int((val - inMin) * (outMax - outMin) / (inMax - inMin) + outMin);

freq = 100
pwm.set_pwm_freq(freq)


print('Now testing...')
steer = 0
gas = 2

steer_mid = 600
steer_max = 800
steer_min = 400

gas_min = 400 #450
gas_max = 800 #850
gas_mid = 600



print('Killing pwm')
pwm.set_pwm(gas, 0, 0)
pwm.set_pwm(steer, 0, 0)


#print('zoom')
#pwm.set_pwm(gas, 0, 700)
#time.sleep(2)
#pwm.set_pwm(gas, 0, 0)
#print('done')

