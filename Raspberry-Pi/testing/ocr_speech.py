import time
import os
from PIL import Image
from picamera2 import Picamera2
from demo_opts import get_device
from gpiozero import Button
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
import numpy as np
import cv2
import pytesseract
from pybraille import convertText

device = get_device()

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(1)

ocr_btn=Button(17)
speech_btn=Button(16)

def perform_ocr(image):
    text = pytesseract.image_to_string(image)
    return text

display_text = False
ocr_text=""

try:
    while True:
        
        if display_text:
            if ocr_btn.is_pressed:
                print("Exiting OCR display mode.")
                display_text = False
                time.sleep(0.3)
            elif speech_btn.is_pressed:
                os.system(f'espeak "{ocr_text}"')
                
            continue
        
        frame = picam2.capture_image()
        ocr_frame = picam2.capture_array()

        oled_frame = frame.resize(device.size).convert(device.mode)
        
        if ocr_btn.is_pressed:
            frame.save("captured_frame.jpg")
            
            english_text = perform_ocr(ocr_frame)
            ocr_text=english_text
            braille_text = convertText(english_text)
            
            with canvas(device) as draw:
                draw.text((0,0), english_text, font=ImageFont.load_default(), fill=255)
                draw.text((0,16), braille_text, font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14), fill=255)
                
            display_text = True
            time.sleep(0.3)
        
        else:
            device.display(oled_frame)

        time.sleep(0.05)  # Adjust to control frame rate
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    picam2.stop()
