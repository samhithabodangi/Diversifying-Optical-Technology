#Code from: https://www.pythoncentral.io/how-to-create-a-website-with-python-for-beginners/

from PIL import Image
import pytesseract
import numpy as np
import cv2

filename = 'captured.jpg'

img = np.array(Image.open(filename))

norm_img = np.zeros((img.shape[0], img.shape[1]))
img = cv2.normalize(img, norm_img, 0, 255, cv2.NORM_MINMAX)
img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)[1]
img = cv2.GaussianBlur(img, (1, 1), 0)

text = pytesseract.image_to_string(img)

cv2.imshow("Processed Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

print(text)
