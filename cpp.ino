#include <Servo.h>
#include <DHT.h>

// Define pins
const int urineSensorPin = A0; // Analog input pin for the moisture sensor
const int digitalPin = 2;      // Digital input pin for the moisture sensor
const int servoPin = 9;        // Pin for the servo motor
const int DHTPin = 7;          // Digital pin connected to the DHT sensor

// Initialize DHT sensor
#define DHTTYPE DHT11   // DHT 11
DHT dht(DHTPin, DHTTYPE);

Servo myServo;

void setup() {
  Serial.begin(9600);
  pinMode(digitalPin, INPUT);
  myServo.attach(servoPin);
  myServo.write(0);  // Initialize the servo position to 0 degrees (cradle stopped)
  
  dht.begin();
  Serial.println("System initialized and ready.");
}

void loop() {
  // Read the temperature and humidity from the DHT sensor
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.print("%  Environmental Temperature: ");
    Serial.print(temperature);
    Serial.println("°C");
  }

  // Read the moisture sensor
  int analogValue = analogRead(urineSensorPin);
  int digitalValue = digitalRead(digitalPin);
  
  Serial.print("Analog Sensor Value: ");
  Serial.print(analogValue);
  Serial.print(", Digital Sensor Value: ");
  Serial.println(digitalValue ? "DRY" : "WET");

  if (digitalValue == LOW) {  // Assuming LOW means "WET"
    Serial.println("Urine Detected! Activating cradle swing.");
    swingCradle();
  } else {
    Serial.println("No urine detected. Stopping cradle.");
    stopCradle();
  }

  delay(2000); // Delay to slow down the loop and make reading easier
}

void swingCradle() {
  Serial.println("Swinging cradle...");

  // Swing from 0 degrees to 45 degrees
  for (int pos = 0; pos <= 45; pos++) {
    myServo.write(pos);
    delay(15);
  }
  // Swing back from 45 degrees to 0 degrees
  for (int pos = 45; pos >= 0; pos--) {
    myServo.write(pos);
    delay(15);
  }
}


void stopCradle() {
  myServo.write(0);
  Serial.println("Cradle stopped.");
}
