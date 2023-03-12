# Temperature Logger
This project originated in the one week block course "Practical Measurement Electronics and Interfaces in Ocean Sciences" taught by Niels Fuchs and Markus Ritschel at the Universität Hamburg.
The Arduino code and data of all temperature loggers as well as a report functioning as a data sheet are contained in this repository. For a better overview about the  files included check [Project Structure](##project-structure).


## About
### Logging Unit
The temperature logger measures temperature every second and writes the last spot and an average value to SD card every 10 seconds.
It uses an Arduino-like microcontroller and a Maxim Integrated DS18B20.

### Python Code
The repository also includes the Python code to calibrate the sensors based on a Greisinger GMH 3700 Series Pt100 High-Precision thermometer reference measurement. It also provides an evaluation of the time constants.

For further information check *Report_Temperature-Logger_QR.pdf*. 
## Preparation
To reproduce the project, clone this repository on your machine:
```bash
git clone https://github.com/QuentinRauschenbach/Temperature_Logger
```
Follow the wiring from the circuit diagram in *pictures* to connect an Arduino to a DS18B20 temperature sensor and upload *Temperature_Logger_Code* to the Arduino.

## Project Structure
```
├── Temperature_Logger_Code          <- Arduino main code + two helpers
│
├── analysis                         <- Python code used for calibration and derivation of the time constant of the sensors
├── data                             <- Contains 9 temperature measurments from DS18B20s and 
│   │                                   Greisinger reference data digitalized from the lab-book.
│   ├── adjusted                     <- DS18B20 data with synchronized time axis
│
├── pictures                         <- Plots produced in Python and circuit 
│
├── Report_Temperature-Logger_QR.pdf <- "Data sheet" for the temperature logger
│
└── README.md               
```

## Contact
For any questions or issues, please contact me via quentin.rauschenbach@studium.uni-hamburg.de



