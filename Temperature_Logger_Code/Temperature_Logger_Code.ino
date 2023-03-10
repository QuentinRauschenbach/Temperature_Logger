/***********************************
 * author: Quentin Rauschenbach
 * 
 * email: quentin.rauschenbach@studium.uni-hamburg.de
 * 
 * UHH WiSe 2022/2023
 * Practical Measurement Electronics and Interfaces in Ocean Sciences
 * 
 * This script uses an Arduino together with a DS18B20 temperature
 * sensor and pure OneWire based communication.
 * 
 ***********************************/
 
#include <SD.h>
#include <SPI.h> // on pin 13
#include <RTClib.h>
#include <OneWire.h>
#include "ds18b20_hex-helper.h"

// User-defined constants
const String logfile = "tsensor.log";
const String header = "# timestamp, millis, sensor_id, temperature in °C with 2 digits (spot, avg)";
float temp_sum = 0;
int cnt = 1;
const float spot_interval = 1.0; // seconds between two spot measurments
const float N = 10;             // number of spot measurments to average over

RTC_DS1307 rtc;             // communication with clock
OneWire ow(4);              // initialise onewire bus on pin4

void setup() {
  Serial.begin(9600);

  if(!rtc.begin()) {        //if begin is not succesful
    Serial.println("RTC is NOT running. Let's set time now");
    rtc.adjust(DateTime(F(__DATE__),F(__TIME__)));
  }
  /*
   * When time needs to be set on a new device or after a power loss the following line 
   * sets the RTC to the date & time this ketch was compiled (!)
   */
  //rtc.adjust(DateTime(F(__DATE__),F(__TIME__)));
  
  if(!SD.begin(10)){        // SD card on pin10
    Serial.println("SD module initialization failed or Card is not present");
    return;
    }
    
  printOutputln(header);
}

void loop() {
  byte rom_code[8];         // creates as array containing 8 elements of type byte for the rom code
  byte sp_data[9];          // scratchpad data
  
  //Start 0. sequence: read out rom code (sensor family on LSB, then 64.bit registration ID)
  ow.reset();               // reset onewire bus
  ow.write(READ_ROM);
  
  for (int i=0; i<8; i++){  // ++ increase by one at the end of the loop
    rom_code[i] = ow.read(); // rom_code = [LSB ... MSB] = [family code (0x28),48-bits (serial nr),CRC]
  }
  
  if(rom_code[0] !=IS_DS18B20_SENSOR){ // if different family code
    Serial.println("Sensor is not a DS18B20");
  }
  String registration_number;
  for (int i=1; i<7; i++){
    registration_number += String(rom_code[i],HEX);//append string store serial number
  }

  // Start sequence: convert temperature
  ow.reset();
  ow.write(SKIP_ROM);
  ow.write(CONVERT_T);      // convert detected value to Temp in °C

  // Start sequence: read data from scratchpad
  ow.reset();
  ow.write(SKIP_ROM);
  ow.write(READ_SCRATCHPAD);
  for (int i=0; i<9; i++){ 
    sp_data[i] = ow.read(); 
  }
  // temp info in the first two bytes
  int16_t tempRead = sp_data[1] << 8 | sp_data[0]; // 8-bit shift & OR-ing -> 16 bit int (1101 1010 .... ....) already takes care of the sign
  float tempCelcius = tempRead / 16.0; // 2**-4 = 16 behind comma 
  
  temp_sum += tempCelcius;
  
  if(cnt%int(N)==0){
    float temp_avg = temp_sum / N ;
    // print timestamp, sensor-id,temperature
    printOutput(getISOtime());
    printOutput(", ");
    printOutput(String(millis()));
    printOutput(", ");
    printOutput(registration_number);
    printOutput(", ");
    printOutput(String(tempCelcius));
    printOutput(", ");
    printOutputln(String(temp_avg));
    
    temp_sum = 0;
  }
 
  
  //set time interval to 1 second
  float next_1000 = (int(millis()/1000) + spot_interval)*1000.0; 
  if (next_1000-millis() < 0) {
    Serial.println("Error!");
  }
  
  delay((int(millis()/1000) + spot_interval)*1000.0-millis()); 

  cnt +=1;
  
  
  
  
  
  

}
