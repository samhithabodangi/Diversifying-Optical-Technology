from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
from gpiozero import Button
import time

# Initialize the button
translateButton = Button(17)

def main():
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial)
    font = ImageFont.load_default()
    
    counter = 0

    while True:
        translateButton.wait_for_press()
        counter += 1
        
        with canvas(device) as draw:
            draw.text((10, 10), f"Button pressed:", font=font, fill=255)
            draw.text((10, 25), f"{counter} times", font=font, fill=255)
        
        time.sleep(0.5)  # Debounce / pause for visibility

if __name__ == "__main__":
    main()
