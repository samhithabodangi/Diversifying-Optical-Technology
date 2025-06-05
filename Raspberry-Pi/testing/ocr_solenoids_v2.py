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
pca_one=PCA9685(i2c, address=0x41)
pca_twothree=PCA9685(i2c, address=0x60)
pca_one.frequency = 100
pca_twothree.frequency = 100

display_text = False

braille = [
    [1,0,0,0,0,0], [1,1,0,0,0,0], [1,0,0,1,0,0], [1,0,0,1,1,0], [1,0,0,0,1,0],
    [1,1,0,1,0,0], [1,1,0,1,1,0], [1,1,0,0,1,0], [0,1,0,1,0,0], [0,1,0,1,1,0], 
    [1,0,1,0,0,0], [1,1,1,0,0,0], [1,0,1,1,0,0], [1,0,1,1,1,0], [1,0,1,0,1,0],  
    [1,1,1,1,0,0], [1,1,1,1,1,0], [1,1,1,0,1,0], [0,1,1,1,0,0], [0,1,1,1,1,0], 
    [1,0,1,0,0,1], [1,1,1,0,0,1], [0,1,0,1,1,1], [1,0,1,1,0,1], [1,0,1,1,1,1], 
    [1,0,1,0,1,1]
]

braille_cells = [
    (pca_one, [0, 1, 2, 3, 4, 5]),        # Cell 1: pca_one
    (pca_twothree, [0, 1, 2, 3, 4, 5]),   # Cell 2: pca_twothree first 6
    (pca_twothree, [6, 7, 8, 9, 10, 11])  # Cell 3: pca_twothree next 6
]
braille_text=""

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(braille_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def set_solenoid_state(pca, channel, state):
    if state:
        pca.channels[channel].duty_cycle = 0xFFFF
    else:
        pca.channels[channel].duty_cycle = 0

def display_char(cell_index, char):
    if not char.isalpha():
        return
    index = ord(char.lower()) - ord('a')
    pca, channels = braille_cells[cell_index]
    for i in range(6):
        set_solenoid_state(pca, channels[i], braille[index][i])

def clear_all_cells():
    for pca, channels in braille_cells:
        for ch in channels:
            set_solenoid_state(pca, ch, 0)

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

            i = 0
            while i < len(braille_text):
                chars = braille_text[i:i+3]
                print(f"\nDisplaying: {chars}")

                for j, c in enumerate(chars):
                    display_char(j, c)

                # Wait for braille_pin press to continue
                print("Waiting for next...")
                while GPIO.input(braille_pin) == 0:
                    time.sleep(0.01)

                time.sleep(0.5)
                clear_all_cells()
                time.sleep(0.2)
                i += 3

except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    picam2.stop()
    clear_all_cells()
    cv2.destroyAllWindows()
    GPIO.cleanup()
