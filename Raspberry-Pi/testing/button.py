from gpiozero import Button

button=Button(17)

button.wait_for_press()
print("The button was Pressed!")
