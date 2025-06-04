import RPi.GPIO as GPIO
import time
from adafruit_pca9685 import PCA9685
from time import sleep
import board
# --- PCA9685 Setup ---
# Your PCA9685 address is 0x60 (decimal 96)
# Initialize ServoKit for 16 channels on your PCA9685
#it = ServoKit(channels=16, address=0x60)

i2c=board.I2C()
pca=PCA9685(i2c, address=0x41)
pca.frequency = 100

# Braille mapping: each sublist represents dots 1-6 for a-z
# (Assuming solenoids are connected to PCA9685 channels 0-5 for dots 1-6 respectively)
braille = [
    [1,0,0,0,0,0],  # a
    [1,1,0,0,0,0],  # b
    [1,0,0,1,0,0],  # c
    [1,0,0,1,1,0],  # d
    [1,0,0,0,1,0],  # e
    [1,1,0,1,0,0],  # f
    [1,1,0,1,1,0],  # g
    [1,1,0,0,1,0],  # h
    [0,1,0,1,0,0],  # i
    [0,1,0,1,1,0],  # j
    [1,0,1,0,0,0],  # k
    [1,1,1,0,0,0],  # l
    [1,0,1,1,0,0],  # m
    [1,0,1,1,1,0],  # n
    [1,0,1,0,1,0],  # o
    [1,1,1,1,0,0],  # p
    [1,1,1,1,1,0],  # q
    [1,1,1,0,1,0],  # r
    [0,1,1,1,0,0],  # s
    [0,1,1,1,1,0],  # t
    [1,0,1,0,0,1],  # u
    [1,1,1,0,0,1],  # v
    [0,1,0,1,1,1],  # w
    [1,0,1,1,0,1],  # x
    [1,0,1,1,1,1],  # y
    [1,0,1,0,1,1],  # z
]

# Define PCA9685 channels for solenoids (assuming channels 0-5)
# IMPORTANT: Map these to the actual channels your solenoids are wired to on the PCA9685
solenoid_channels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]

# Define Raspberry Pi GPIO pin for the button
button_pin = 17 # BCM mode pin number

# The text to convert to braille
text = "absolute"

# --- Setup GPIO for Button ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# --- Function to activate/deactivate a solenoid dot ---
def set_solenoid_state(channel, state):
    """
    Sets the state of a solenoid connected to a PCA9685 channel.
    state: 1 for ON (dot up), 0 for OFF (dot down)
    """
    if state == 1:
        # Solenoid ON (dot up) - set throttle to 1 (full forward)
        pca.channels[channel].duty_cycle=0xFFFF
    else:
        # Solenoid OFF (dot down) - set throttle to 0 (stop)
        pca.channels[channel].duty_cycle=0 # Using 0.0 for clarity, can also be None

# --- Main loop for Braille display ---
try:
    # Ensure all solenoids are off initially
    for channel in solenoid_channels:
        set_solenoid_state(channel, 0) # Turn all solenoids off
    time.sleep(0.5) # Give them a moment to retract
    
    i = 0
    while i < len(text) - 1:
        char1 = text[i].lower()
        char2 = text[i + 1].lower()
        
        if char1.isalpha() and char2.isalpha():
            index_one = ord(char1) - ord('a')
            index_two = ord(char2) - ord('a')
            print(f"\nDisplaying: '{char1}{char2}' (Braille Indices: {index_one}, {index_two})")

            for j in range(6):  # 6 dots per cell
                channel_first = solenoid_channels[j]
                channel_second = solenoid_channels[j + 6]

                dot_state_first = braille[index_one][j]
                dot_state_second = braille[index_two][j]

                set_solenoid_state(channel_first, dot_state_first)
                set_solenoid_state(channel_second, dot_state_second)
                
            # Wait for button pres
            while GPIO.input(button_pin) == 0:
                time.sleep(0.01) # Check button state frequently

            # A short pause before the next letter, after button release
            time.sleep(1)
        i += 2

except KeyboardInterrupt:
    print("\nProgram interrupted.")

finally:
    for channel in solenoid_channels:
        set_solenoid_state(channel, 0)
    GPIO.cleanup()
