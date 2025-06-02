// Flashlight pin on ESP32-CAM
const int FLASH_PIN = 4;
// Button input pin (you can change this)
const int BUTTON_PIN = 12;

void setup() {
  pinMode(FLASH_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);  // use internal pull-up resistor
  digitalWrite(FLASH_PIN, LOW);       // flashlight off initially
}

void loop() {
  // Read the button state (LOW when pressed)
  int buttonState = digitalRead(BUTTON_PIN);

  if (buttonState == LOW) {
    digitalWrite(FLASH_PIN, HIGH);  // turn on flashlight
  } else {
    digitalWrite(FLASH_PIN, LOW);   // turn off flashlight
  }

  delay(10); // small debounce delay
}
