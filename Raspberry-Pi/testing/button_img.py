from picamzero import Camera
from time import sleep
from gpiozero import Button 

button=Button(17)
cam=Camera()

cam.start_preview()
button.wait_for_press()
print("The button was Pressed!")

cam.take_photo("image.jpg")
cam.stop_preview()
