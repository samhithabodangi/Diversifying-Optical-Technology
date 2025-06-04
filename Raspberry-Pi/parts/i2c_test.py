from adafruit_pca9685 import PCA9685
from time import sleep
import time
import board

# Create the I2C bus interface.
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = busio.I2C(board.GP1, board.GP0)    # Pi Pico RP2040

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c, address=0x60)

# Set the PWM frequency to 60hz.
pca.frequency = 100

# Set the PWM duty cycle for channel zero to 50%. duty_cycle is 16 bits to match other PWM objects
# but the PCA9685 will only actually give 12 bits of resolution.
pca.channels[5].duty_cycle = 0xFFFF
time.sleep(5)
pca.channels[5].duty_cycle=0

# but the PCA9685 will only actually give 12 bits of resolution.
pca.channels[0].duty_cycle = 0xFFFF
time.sleep(5)
pca.channels[0].duty_cycle=0
