/***********************************
 * author: Quentin Rauschenbach
 * 
 * email: quentin.g.j.r@gmail.com
 * 
 * UHH WiSe 2022/2023
 * Practical Measurement Electronics and Interfaces in ocean Sciences
 * 
 * This script uses an Arduino together with a DS18B20 temperature
 * sensor and pure OneWire based communication.
 * 
 ***********************************/

#include <SD.h>
#include <SPI.h>
#include <RTClib.h>
#include <OneWire.h>

RTC_DS1307 rtc; // communication with clock

OneWire ow(4); //onewire(Pin4) bus initialisation


void setup() {
  Serial.begin(9600);

  if(!rtc.begin()) {//if begin is not succesful
    Serial.println("RTC is NOT running. Let's set time now");
    rtc.adjust(DateTime(F(__DATE__),F(__TIME__)));
  }
  
  if(!SD.begin(10)){
    Serial.println("SD module initialization failed or Card is not present");
    return;
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}
