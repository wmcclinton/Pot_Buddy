#include <OneWire.h>
#include <DallasTemperature.h>

String readString;

String mode = "REST";

int duration = 100;
 
int photocellPin = 0;     // the cell and 10K pulldown are connected to a0
int photocellPin2 = 1;     // the cell and 10K pulldown are connected to a0
int photocellPin3 = 2;     // the cell and 10K pulldown are connected to a0
int photocellPin4 = 3;     // the cell and 10K pulldown are connected to a0
int moistureSensor = 4;

int photocellReading;     // the analog reading from the sensor divider
int photocellReading2;     // the analog reading from the sensor divider
int photocellReading3;     // the analog reading from the sensor divider
int photocellReading4;     // the analog reading from the sensor divider
int moistureReading;
double tempReading;


// Data wire is conntec to the Arduino digital pin 2
#define ONE_WIRE_BUS 2

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);

// Pass our oneWire reference to Dallas Temperature sensor 
DallasTemperature sensors(&oneWire);

// Motor functions
void RForward(){
  digitalWrite(7, LOW);
  digitalWrite(6, HIGH);
  digitalWrite(5, HIGH);
}

void RBackward(){
  digitalWrite(7, HIGH);
  digitalWrite(6, LOW);
  digitalWrite(5, HIGH);
}

void RStop(){
  digitalWrite(7, LOW);
  digitalWrite(6, LOW);
  digitalWrite(5, LOW);
}

void LForward(){
  digitalWrite(8, HIGH);
  digitalWrite(9, LOW);
  digitalWrite(10, HIGH);
}

void LBackward(){
  digitalWrite(8, LOW);
  digitalWrite(9, HIGH);
  digitalWrite(10, HIGH);
}

void LStop(){
  digitalWrite(8, LOW);
  digitalWrite(9, LOW);
  digitalWrite(10, LOW);
}

void Stop(){
  RStop();
  LStop();
}

void Forward(){
  RForward();
  LForward();
  delay(duration);
  Stop();
}

void Backward(){
  RBackward();
  LBackward();
  delay(duration);
  Stop();
}

void TurnLeft(){
  RForward();
  LBackward();
  delay(duration);
  Stop();
}

void TurnRight(){
  RBackward();
  LForward();
  delay(duration);
  Stop();
}


void setup() {
  Serial.begin(9600);
  // Writes to Pi
  Serial.println("Arduino Initialized...");
  sensors.begin();

  // Left Motor
  pinMode(8, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);

  // Right Motor
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, OUTPUT);
}

void loop() {

  // Gets characters from Pi
  while (Serial.available()) {
    char c = Serial.read();
    readString += c;
    delay(2);

    // Get Light
    photocellReading = analogRead(photocellPin);  
    photocellReading2 = analogRead(photocellPin2); 
    photocellReading3 = analogRead(photocellPin3);  
    photocellReading4 = analogRead(photocellPin4);

    // Perform Action
    if(mode == "GOLIGHT"){
      // Find Brightest Side
      int sides[] = {photocellReading + photocellReading2, photocellReading + photocellReading3, photocellReading2 + photocellReading4, photocellReading3 + photocellReading4};
      int max_side = 0;
      for(int i = 1; i < 4; i++) {
        if(sides[i] > sides[max_side]){
          max_side = i;
        }
      }

      // Moves
      if(sides[0] == sides[1] && sides[2] == sides[3] && sides[0] == sides[2]){
         Forward();
      } else {
         switch (max_side) {
          case 0:
            Backward();
            break;
          case 1:
            TurnLeft();
            break;
          case 2:
            TurnRight();
            break;
           case 3:
            Forward();
            break;
         }
      }
      
    } else if (mode == "GODARK") {
      // Find Darkest Side
      int sides[] = {photocellReading + photocellReading2, photocellReading + photocellReading3, photocellReading2 + photocellReading4, photocellReading3 + photocellReading4};
      int min_side = 0;
      for(int i = 1; i < 4; i++) {
        if(sides[i] < sides[min_side]){
          min_side = i;
        }
      }

      // Moves
      if(sides[0] == sides[1] && sides[2] == sides[3] && sides[0] == sides[2]){
         Forward();
      } else {
         switch (min_side) {
          case 0:
            Backward();
            break;
          case 1:
            TurnLeft();
            break;
          case 2:
            TurnRight();
            break;
           case 3:
            Forward();
            break;
         }
      }
    }
  }

  // Upload data after all characters read
  if (readString.length() >0) {
    // Preform action based on string read from the Pi
    //
    //
    
    mode = readString;
    
    // Get sensor data
    // Get Light
    photocellReading = analogRead(photocellPin);  
    photocellReading2 = analogRead(photocellPin2); 
    photocellReading3 = analogRead(photocellPin3);  
    photocellReading4 = analogRead(photocellPin4);
    // Get Moisture
    moistureReading = map(analogRead(moistureSensor), 1023, 0, 0, 100);;
    // Get Temp
    sensors.requestTemperatures();
    tempReading = sensors.getTempFByIndex(0);
    
    // Print data to pi
    Serial.println(mode + "-" + String(photocellReading) + "/" + String(photocellReading2)  + "/" + String(photocellReading3) + "/" + String(photocellReading4) +"-" + String(tempReading) + "-" + String(moistureReading));
    delay(100);
    
    readString="";
  } 
}
