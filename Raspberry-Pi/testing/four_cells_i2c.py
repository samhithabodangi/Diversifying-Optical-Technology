import RPi.GPIO as GPIO
import time
from adafruit_pca9685 import PCA9685
from time import sleep
import board

i2c=board.I2C()
pca_onetwo=PCA9685(i2c, address=0x41)
pca_threefour=PCA9685(i2c, address=0x60)
pca_onetwo.frequency = 100
pca_threefour.frequency = 100

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

braille_cells = [
    (pca_onetwo, [0, 1, 2, 3, 4, 5]),       # Cell 1
    (pca_onetwo, [6, 7, 8, 9, 10, 11]),     # Cell 2
    (pca_threefour, [0, 1, 2, 3, 4, 5]),    # Cell 3
    (pca_threefour, [6, 7, 8, 9, 10, 11])   # Cell 4     
]

button_pin = 17 
text = "jeopardizing"

space = [0,0,0,0,0,0]

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def set_solenoid_state(pca, channel, state):
    if state:
        pca.channels[channel].duty_cycle = 0xFFFF
    else:
        pca.channels[channel].duty_cycle = 0

def display_char(cell_index, char):
    if not char.isalpha():
        return
    index = ord(char.lower()) - ord('a')
    pca, channels = braille_cells[cell_index]
    for i in range(6):
        set_solenoid_state(pca, channels[i], braille[index][i])

def clear_all_cells():
    for pca, channels in braille_cells:
        for ch in channels:
            set_solenoid_state(pca, ch, 0)

try:
    clear_all_cells()
    time.sleep(0.5)
    
    i = 0
    while i < len(text):
        chars = text[i:i+4]
        print(f"\nDisplaying: {chars}")

        for j, c in enumerate(chars):
            display_char(j, c)
            
        while GPIO.input(button_pin) == 0:
            time.sleep(0.01)

        time.sleep(0.5)

        i += 4


except KeyboardInterrupt:
    print("\nProgram interrupted.")

finally:
    clear_all_cells()
    GPIO.cleanup()
