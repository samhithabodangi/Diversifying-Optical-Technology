from adafruit_servokit import ServoKit
from time import sleep
kit = ServoKit(channels=16,address=0x60)


def servo1():
    for a in range(0,180):
        kit.servo[5].angle = a
        sleep(0.008)
        
    for a in range(179,1,-1):
        kit.servo[0].angle = a
        sleep(0.008)
        
def servo2():
    for a in range(0,180):
        kit.servo[1].angle = a
        sleep(0.008)
        
    for a in range(179,1,-1):
        kit.servo[1].angle = a
        sleep(0.008)
        
while True:
    servo1()
    servo2()
