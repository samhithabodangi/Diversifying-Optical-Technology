import RPi.GPIO as GPIO
import time
from adafruit_pca9685 import PCA9685
from time import sleep
import board

i2c=board.I2C()
pca_onetwo=PCA9685(i2c, address=0x60)
pca_threefour=PCA9685(i2c, address=0x41)
pca_onetwo.frequency = 100
pca_threefour.frequency = 100

braille_letters = [
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

braille_punctuation = [
    (',', [0, 1, 0, 0, 0, 0]),
    (';', [0, 1, 1, 0, 0, 0]),
    (':', [0, 1, 0, 0, 1, 0]),
    ('.', [0, 1, 0, 0, 1, 1]),
    ('!', [0, 1, 1, 0, 1, 0]),
    ('(', [0, 1, 1, 0, 1, 0]),
    (')', [0, 1, 1, 0, 1, 0]),
    ('?', [0, 1, 1, 0, 0, 1]),
    ('*', [0, 0, 1, 0, 1, 0]),
    ('"', [0, 0, 1, 0, 1, 1]),
]


braille_numbers = [
    ('1', [1,0,0,0,0,0]),
    ('2', [1,1,0,0,0,0]),
    ('3', [1,0,0,1,0,0]),
    ('4', [1,0,0,1,1,0]),
    ('5', [1,0,0,0,1,0]),
    ('6', [1,1,0,1,0,0]),
    ('7', [1,1,0,1,1,0]),
    ('8', [1,1,0,0,1,0]),
    ('9', [0,1,0,1,0,0]),
    ('0', [0,1,0,1,1,0]),
]

captial = [0,0,0,0,0,1]  
number  = [0,0,1,1,1,1] 
space = [0,0,0,0,0,0]

braille_cells = [
    (pca_onetwo, [0, 1, 2, 3, 4, 5]),       # Cell 1
    (pca_onetwo, [6, 7, 8, 9, 10, 11]),     # Cell 2
    (pca_threefour, [0, 1, 2, 3, 4, 5]),    # Cell 3
    (pca_threefour, [6, 7, 8, 9, 10, 11])   # Cell 4     
]

braille_pin = 17 
braille_text = "Hello, 2 you!"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(braille_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def set_solenoid_state(pca, channel, state):
    if state:
        pca.channels[channel].duty_cycle = 0xFFFF
    else:
        pca.channels[channel].duty_cycle = 0

def display_char(cell_index, dataset):
    pca, channels = braille_cells[cell_index]
    for i in range(6):
        set_solenoid_state(pca, channels[i], dataset[i])

def check_char(cell_index, char):
    if char == ' ':
        display_char(cell_index, space)
        return
    
    if char.isupper():
        display_char(cell_index, captial)
        time.sleep(0.5)
        char = char.lower()

    if char.isdigit():
        display_char(cell_index, number)
        time.sleep(0.5)

        digit_pattern = None
        for digit, pattern in braille_numbers:
            if char == digit:
                digit_pattern = pattern
        if digit_pattern:
            display_char(cell_index, digit_pattern)
    
    if char.isalpha():
        index = ord(char) - ord('a')
        display_char(cell_index, braille_letters[index])
        return
    
    else:
        punct_pattern = None
        for symbol, pattern in braille_punctuation:
            if char == symbol:
                punct_pattern = pattern
                break
        if punct_pattern:
            display_char(cell_index, punct_pattern)

def clear_all_cells():
    for pca, channels in braille_cells:
        for ch in channels:
            set_solenoid_state(pca, ch, 0)

def perform_ocr(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

try:
    while True:
        
        i = 0
        while i < len(braille_text):
            chars = braille_text[i:i+4]
            print(f"\nDisplaying: {chars}")

            for j in range(4):
                if j < len(chars):
                    check_char(j, chars[j])
                else:
                    # Clear the unused cell
                    display_char(j, space)

            print("Waiting for next...")
            while GPIO.input(braille_pin) == 0:
                time.sleep(0.01)

            time.sleep(0.5)
            i += 4
                

except KeyboardInterrupt:
    print("\nProgram interrupted.")

finally:
    clear_all_cells()
    GPIO.cleanup()
