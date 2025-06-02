from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
import time

def main():
        # Create I2C interface
        serial = i2c(port=1, address=0x3C)

        # Create device
        device = ssd1306(serial)

        # Use a truetype font or the default one if not available
        try:
                font = ImageFont.truetype("arial.ttf", 16)
        except IOError:
                font = ImageFont.load_default()

        # Draw "Hello World" on the OLED display
        while True:
                with canvas(device) as draw:
                        draw.text((10, 10), "Hello World", font=font, fill=255)
                time.sleep(1)


if __name__ == "__main__":
    main()
