const int LEDpin =9;
const int butpin =2;
int state;

void setup() {
  pinMode(LEDpin, OUTPUT);
  pinMode(butpin, INPUT_PULLUP);
}

void loop() {
  state = digitalRead(butpin);

  if (state == HIGH) {
    digitalWrite(LEDpin, 0);
  }
  else{
    digitalWrite(LEDpin, 128);
  }
}
