from picamera2 import Picamera2
import time
import numpy as np
import cv2
import pytesseract

# Initialize the camera
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (640, 480)}))
picam2.start()
time.sleep(1)  # Allow camera to warm up

while True:
    # Capture a frame as a numpy array
    frame = picam2.capture_array()

    # Perform OCR
    text = pytesseract.image_to_string(frame)

    # Show the frame
    cv2.imshow("Frame", frame)
    print(text)

    # Wait for key press
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

