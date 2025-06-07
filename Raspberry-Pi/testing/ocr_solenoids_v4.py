import os
from PIL import Image, ImageFont
from picamera2 import Picamera2
from gpiozero import Button
import numpy as np
import cv2
import pytesseract
from pybraille import convertText
from libcamera import controls
import RPi.GPIO as GPIO
import time
from adafruit_pca9685 import PCA9685
from time import sleep
import board
from demo_opts import get_device
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

device = get_device()

camera = Picamera2()
config = camera.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"
                                                   })
camera.configure(config)
camera.start()
camera.set_controls({"AfMode":controls.AfModeEnum.Continuous})

time.sleep(1)

ocr_btn=Button(27)
braille_pin = 17

display_text=False
braille_text = ""

i2c=board.I2C()
pca_onetwo=PCA9685(i2c, address=0x60)
pca_threefour=PCA9685(i2c, address=0x41)
pca_onetwo.frequency = 100
pca_threefour.frequency = 100

braille_letters = [
    [1,0,0,0,0,0],  # a
    [1,1,0,0,0,0],  # b
    [1,0,0,1,0,0],  # c
    [1,0,0,1,1,0],  # d
    [1,0,0,0,1,0],  # e
    [1,1,0,1,0,0],  # f
    [1,1,0,1,1,0],  # g
    [1,1,0,0,1,0],  # h
    [0,1,0,1,0,0],  # i
    [0,1,0,1,1,0],  # j
    [1,0,1,0,0,0],  # k
    [1,1,1,0,0,0],  # l
    [1,0,1,1,0,0],  # m
    [1,0,1,1,1,0],  # n
    [1,0,1,0,1,0],  # o
    [1,1,1,1,0,0],  # p
    [1,1,1,1,1,0],  # q
    [1,1,1,0,1,0],  # r
    [0,1,1,1,0,0],  # s
    [0,1,1,1,1,0],  # t
    [1,0,1,0,0,1],  # u
    [1,1,1,0,0,1],  # v
    [0,1,0,1,1,1],  # w
    [1,0,1,1,0,1],  # x
    [1,0,1,1,1,1],  # y
    [1,0,1,0,1,1],  # z
]

braille_punctuation = [
    (',', [0, 1, 0, 0, 0, 0]),
    (';', [0, 1, 1, 0, 0, 0]),
    (':', [0, 1, 0, 0, 1, 0]),
    ('.', [0, 1, 0, 0, 1, 1]),
    ('!', [0, 1, 1, 0, 1, 0]),
    ('(', [0, 1, 1, 0, 1, 0]),
    (')', [0, 1, 1, 0, 1, 0]),
    ('?', [0, 1, 1, 0, 0, 1]),
    ('*', [0, 0, 1, 0, 1, 0]),
    ('"', [0, 0, 1, 0, 1, 1]),
]


braille_numbers = [
    ('1', [1,0,0,0,0,0]),
    ('2', [1,1,0,0,0,0]),
    ('3', [1,0,0,1,0,0]),
    ('4', [1,0,0,1,1,0]),
    ('5', [1,0,0,0,1,0]),
    ('6', [1,1,0,1,0,0]),
    ('7', [1,1,0,1,1,0]),
    ('8', [1,1,0,0,1,0]),
    ('9', [0,1,0,1,0,0]),
    ('0', [0,1,0,1,1,0]),
]

captial = [0,0,0,0,0,1]  
number  = [0,0,1,1,1,1] 
space = [0,0,0,0,0,0]

braille_cells = [
    (pca_onetwo, [0, 1, 2, 3, 4, 5]),       # Cell 1
    (pca_onetwo, [6, 7, 8, 9, 10, 11]),     # Cell 2
    (pca_threefour, [0, 1, 2, 3, 4, 5]),    # Cell 3
    (pca_threefour, [6, 7, 8, 9, 10, 11])   # Cell 4     
]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(braille_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def set_solenoid_state(pca, channel, state):
    if state:
        pca.channels[channel].duty_cycle = 0xFFFF
    else:
        pca.channels[channel].duty_cycle = 0

def display_char(cell_index, dataset):
    pca, channels = braille_cells[cell_index]
    for i in range(6):
        set_solenoid_state(pca, channels[i], dataset[i])

def clear_all_cells():
    for pca, channels in braille_cells:
        for ch in channels:
            set_solenoid_state(pca, ch, 0)

def perform_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

try:
    while True:
        
        if display_text:
            if ocr_btn.is_pressed:
                print("Exiting OCR display mode.")
                display_text = False
                time.sleep(0.3) 
            continue
        
        frame = camera.capture_image()
        ocr_frame=camera.capture_array()
        oled_frame = frame.resize(device.size).convert(device.mode)
    
        if ocr_btn.is_pressed:
                
                braille_text = perform_ocr(ocr_frame)
                oled_braille_text = convertText(braille_text)
                
                with canvas(device) as draw:
                    draw.text((0,0), braille_text, font=ImageFont.load_default(), fill=255)
                    draw.text((0,16), oled_braille_text, font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14), fill=255)
                
                display_text=True
                time.sleep(0.3)
                
        else:
            device.display(oled_frame)
        
        i = 0
        while i < len(braille_text):
            total_cells = []
            
            while len(total_cells)< 4 and i < len(braille_text):
                char = braille_text[i]
                
                if char == " ":
                    total_cells.append(space)
                    i += 1
                    continue
                
                if char.isupper():
                    total_cells.append(captial)
                    char = char.lower()
                    
                if char.isdigit():
                    total_cells.append(number)
                    for digit, pattern in braille_numbers:
                        if char == digit:
                            total_cells.append(pattern)
                            break
                    i += 1
                    continue
                
                elif char.isalpha():
                    index = ord(char) - ord('a')
                    total_cells.append(braille_letters[index])
                    i += 1
                    continue

                else:
                    for symbol, pattern in braille_punctuation:
                        if char == symbol:
                            total_cells.append(pattern)
                            break
                    i += 1
                
            while len(total_cells) < 4:
                total_cells.append(space)

            for j in range(4):
                display_char(j, total_cells[j])

            print("Waiting for next...")
            while GPIO.input(braille_pin) == 0:
                time.sleep(0.01)

            time.sleep(0.5)
            
        clear_all_cells()

except KeyboardInterrupt:
    print("\nProgram interrupted.")

finally:
    clear_all_cells()
    camera.stop()
    GPIO.cleanup()
