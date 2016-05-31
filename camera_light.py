import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

CAMLED=32

GPIO.setup(CAMLED,GPIO.OUT,initial=False)

for i in range(5):
  GPIO.output(CAMLED,True)
  time.sleep(0.5)
  GPIO.output(CAMLED,False)
  time.sleep(0.5)
