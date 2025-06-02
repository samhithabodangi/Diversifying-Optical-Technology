from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageFont
import time
from pybraille import convertText  # Braille converter
from PIL import ImageFont


def main():
    # Create I2C interface
    serial = i2c(port=1, address=0x3C)

    # Create OLED device
    device = ssd1306(serial)

    # Use a default font (or replace with TTF if needed)
    font = ImageFont.load_default()
    braille_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)

    # Text to display
    text = "Hello"
    braille = convertText(text)

    while True:
        with canvas(device) as draw:
            draw.text((0, 0), text, font=font, fill=255)        # Line 1: English
            draw.text((0, 16), braille, font=braille_font, fill=255)     # Line 2: Braille
        time.sleep(1)

if __name__ == "__main__":
    main()
