#include <Servo.h>
#include <DHT.h>

# Define pins
const int digitalPin = 2;       # Digital input pin for the moisture sensor
const int servoPin = 9;         # Pin for the first servo motor
const int servoPin2 = 10;       # Pin for the second servo motor
const int DHTPin = 7;           # DHT11 sensor pin
#define DHTTYPE DHT11           // DHT sensor type

DHT dht(DHTPin, DHTTYPE);
Servo myServo;
Servo mySecondServo;

enum Mode { AUTO, MANUAL_ON, MANUAL_OFF };
Mode swingMode = AUTO;

bool systemActive = true;  # Control flag for POWER_ON / POWER_OFF

void setup() {
  Serial.begin(9600);
  pinMode(digitalPin, INPUT);
  myServo.attach(servoPin);
  mySecondServo.attach(servoPin2);
  myServo.write(90);  # Initial position - Middle
  mySecondServo.write(90); # Initial position - Middle
  dht.begin();
  Serial.println("System initialized. Default mode set to AUTO.");
}

void loop() {
  # Handle serial input
  handleSerial();

  # Only run system if active
  if (systemActive) {
    # Read DHT sensor data
    float humidity = dht.readHumidity();
    float temperature = dht.readTemperature();
   
    # Send DHT sensor data over serial
    if (!isnan(humidity) && !isnan(temperature)) {
      Serial.print("DHT,");
      Serial.print(humidity);
      Serial.print(",");
      Serial.println(temperature);
    } else {
      Serial.println("Failed to read from DHT sensor!");
    }

    # Read moisture sensor status
    int digitalValue = digitalRead(digitalPin);
    Serial.print("Moisture Sensor Status: ");
    Serial.println(digitalValue == LOW ? "Wet" : "Dry");

    # Execute swing control logic based on mode
    switch(swingMode) {
      case AUTO:
        if (digitalValue == LOW) { # If moisture detected
          swingCradle();
        } else {
          stopCradle();
        }
        break;
      case MANUAL_ON:
        swingCradle();
        break;
      case MANUAL_OFF:
        stopCradle();
        break;
    }
  }

  delay(1000); # Delay between loops to reduce sensor reading frequency
}

void handleSerial() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
   
    if (command == "SWING_ON") {
      swingMode = MANUAL_ON;
      Serial.println("Mode set to MANUAL_ON.");
    } else if (command == "SWING_OFF") {
      swingMode = MANUAL_OFF;
      Serial.println("Mode set to MANUAL_OFF.");
    } else if (command == "SWING_AUTO") {
      swingMode = AUTO;
      Serial.println("Mode set to AUTO.");
    } else if (command == "POWER_OFF") {
      stopCradle();
      systemActive = false;
      Serial.println("System deactivated by POWER_OFF.");
    } else if (command == "POWER_ON") {
      systemActive = true;
      Serial.println("System reactivated by POWER_ON.");
    }
  }
}

void swingCradle() {
  Serial.println("Swinging Cradle...");
  for (int pos = 90; pos <= 120; pos++) {
    myServo.write(pos);
    mySecondServo.write(180 - pos);
    delay(15);
  }
  for (int pos = 120; pos >= 65; pos--) {
    myServo.write(pos);
    mySecondServo.write(180 - pos);
    delay(15);
  }
  for (int pos = 65; pos <= 90; pos++) {
    myServo.write(pos);
    mySecondServo.write(180 - pos);
    delay(15);
  }
}

void stopCradle() {
  myServo.write(90);
  mySecondServo.write(90);
  Serial.println("Cradle stopped.");
}