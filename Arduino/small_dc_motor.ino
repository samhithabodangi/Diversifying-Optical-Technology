// Motor connected to digital pin 9 (PWM-capable)
const int motorPin = 9;

// Encoder pins
const int encoderA = 2;  // Interrupt-capable
const int encoderB = 3;

volatile long encoderCount = 0;

void setup() {
  pinMode(motorPin, OUTPUT);
  pinMode(encoderA, INPUT);
  pinMode(encoderB, INPUT);

  attachInterrupt(digitalPinToInterrupt(encoderA), encoderISR, CHANGE);

  Serial.begin(9600);

  digitalWrite(motorPin, HIGH);  // Start motor immediately
}

void loop() {
  // Print encoder count periodically
  Serial.print("Encoder Count: ");
  Serial.println(encoderCount);
  delay(500);  // Adjust refresh rate as needed
}

void encoderISR() {
  int a = digitalRead(encoderA);
  int b = digitalRead(encoderB);
  if (a == b) {
    encoderCount++;
  } else {
    encoderCount--;
  }
}
