from picamera2 import Picamera2
import time
import cv2
import pytesseract
from libcamera import controls

# Initialize camera
picam2 = Picamera2()

# Use a decent preview resolution for a smooth preview and good OCR
preview_config = picam2.create_preview_configuration(main={"size": (1280, 720), "format": "RGB888"})
picam2.configure(preview_config)
picam2.start()
picam2.set_controls({"AfMode":controls.AfModeEnum.Continuous})

time.sleep(1)  # Allow camera to warm up

print("Starting preview with OCR. Press 'q' to quit.")

while True:
    # Capture frame as numpy array
    frame = picam2.capture_array()
    # Run OCR on the processed image
    text = pytesseract.image_to_string(frame)

    # Display preview window
    cv2.imshow("Camera Preview", frame)

    # Print OCR text (can slow down loop if text is large)
    print("Detected Text:", text.strip())

    # Quit if 'q' pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
