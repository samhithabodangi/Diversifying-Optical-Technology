#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Capture continuous video stream with picamera2 and display it on a screen.

import time
from PIL import Image
from picamera2 import Picamera2
from demo_opts import get_device

# Initialize display
device = get_device()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (320, 240)})
picam2.configure(config)
picam2.start()
time.sleep(1)  # Let camera warm up

print("Streaming video to display. Press Ctrl+C to exit.")

try:
    while True:
        # Capture image from camera
        frame = picam2.capture_image()

        # Resize to match display resolution
        frame = frame.resize(device.size).convert(device.mode)

        # Display on screen
        device.display(frame)

        time.sleep(0.05)  # Adjust to control frame rate
except KeyboardInterrupt:
    print("\nStopped by user.")
finally:
    picam2.stop()
