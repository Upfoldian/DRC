# === MOVEMENT STUFF ===
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
freq = 100
pwm.set_pwm_freq(freq)
#Channels
steer     = 0
gas       = 2
relay     = 3
# Steering
steer_mid = 600
steer_max = 800
steer_min = 400
# Gas
gas_min = 400 #450
gas_max = 800 #850


def map_pulse(val, inMin, inMax, outMin, outMax):
    return int((val - inMin) * (outMax - outMin) / (inMax - inMin) + outMin);

