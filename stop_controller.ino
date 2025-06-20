const int STOP_PIN = 8;
const int LED_PIN = 13;

void setup() {
  pinMode(STOP_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);
  
  // Initialize in moving state
  digitalWrite(STOP_PIN, LOW);
  digitalWrite(LED_PIN, LOW);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    if (command == '1') {
      // Stop command
      digitalWrite(STOP_PIN, HIGH);
      digitalWrite(LED_PIN, HIGH);
    } else if (command == '0') {
      // Go command
      digitalWrite(STOP_PIN, LOW);
      digitalWrite(LED_PIN, LOW);
    }
    
    // Clear any remaining bytes in buffer
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
}