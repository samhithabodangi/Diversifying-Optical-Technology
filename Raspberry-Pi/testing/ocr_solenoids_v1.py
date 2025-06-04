import time
import os
from PIL import Image
from picamera2 import Picamera2
from gpiozero import Button
from PIL import ImageFont
import numpy as np
import cv2
import pytesseract
from libcamera import controls

import RPi.GPIO as GPIO
from adafruit_pca9685 import PCA9685
from time import sleep
import board

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
picam2.configure(config)
picam2.start()
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})

time.sleep(1)

ocr_btn=Button(27)
braille_pin = 17

i2c=board.I2C()
pca=PCA9685(i2c, address=0x41)
pca.frequency = 100

display_text = False
ocr_text=""

braille = [
    [1,0,0,0,0,0], [1,1,0,0,0,0], [1,0,0,1,0,0], [1,0,0,1,1,0], [1,0,0,0,1,0],
    [1,1,0,1,0,0], [1,1,0,1,1,0], [1,1,0,0,1,0], [0,1,0,1,0,0], [0,1,0,1,1,0], 
    [1,0,1,0,0,0], [1,1,1,0,0,0], [1,0,1,1,0,0], [1,0,1,1,1,0], [1,0,1,0,1,0],  
    [1,1,1,1,0,0], [1,1,1,1,1,0], [1,1,1,0,1,0], [0,1,1,1,0,0], [0,1,1,1,1,0], 
    [1,0,1,0,0,1], [1,1,1,0,0,1], [0,1,0,1,1,1], [1,0,1,1,0,1], [1,0,1,1,1,1], 
    [1,0,1,0,1,1]
]

solenoid_channels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

braille_text=""

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(braille_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def set_solenoid_state(channel, state):
    if state == 1:
        pca.channels[channel].duty_cycle=0xFFFF
    else:
        pca.channels[channel].duty_cycle=0

def reset_solenoids():
    for channel in solenoid_channels:
            set_solenoid_state(channel, 0) 

try:
    while True:
        frame = picam2.capture_array()
        cv2.imshow("Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        if ocr_btn.is_pressed:
            braille_text = pytesseract.image_to_string(frame)
            print(f"Processed text is:{braille_text}")
            time.sleep(0.3)

        time.sleep(0.05)  

        i = 0
        while i <len(braille_text) -1:
            char1=braille_text[i].lower()
            char2 = braille_text[i+1].lower()

            if char1.isalpha() and char2.isalpha():
                index_one=ord(char1)-ord('a')
                index_two=ord(char2)-ord('a')
                print(f"\nDisplaying: '{char1}{char2}' (Braille Indices: {index_one}, {index_two})")

                for j in range(6):
                    set_solenoid_state(solenoid_channels[j], braille[index_one][j])
                    set_solenoid_state(solenoid_channels[j+6], braille[index_two][j])
                
                while GPIO.input(braille_pin) == 0:
                    time.sleep(0.01)

                time.sleep(1)
            i+=2

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    picam2.stop()
    reset_solenoids()
    cv2.destroyAllWindows()
    GPIO.cleanup()
