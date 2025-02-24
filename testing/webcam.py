#Code from: https://github.com/ESP32-Work/Text-Recognition-ESP32-CAM

import cv2
import urllib.request
import numpy as np
import pytesseract

# Set the path to your Tesseract executable
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'  # Replace with your Tesseract path

# change the IP address below according to the
# IP shown in the Serial monitor of Arduino code
url = 'http://192.168.5.218/capture'

# Increase the window size
cv2.namedWindow("ESP32-CAM Live Stream", cv2.WINDOW_NORMAL)
cv2.resizeWindow("ESP32-CAM Live Stream", 480, 320)  # Adjust the size as needed

while True:
    img_resp = urllib.request.urlopen(url)
    imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
    frame = cv2.imdecode(imgnp, -1)

    # Extract text using Tesseract
    text = pytesseract.image_to_string(frame, config='--psm 6')

    # Display the live stream with extracted text
    cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("ESP32-CAM Live Stream", frame)

    # Print the text serially
    print("Extracted Text:", text)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cv2.destroyAllWindows()