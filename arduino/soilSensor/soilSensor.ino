#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include "Adafruit_Si7021.h"
#include "SparkFun_SCD30_Arduino_Library.h"
#include "Zanshin_BME680.h" // Include the BME680 Sensor library
#include <arduino-timer.h>

#define ARDUINOJSON_USE_LONG_LONG 1
#include <ArduinoJson.h>


//#define TEMP_1        PA8
//#define TEMP_2        PB6
//#define TEMP_3        PA6
//#define TEMP_4        PA7
//#define TEMP_5        PB2

#define TEMP          6 //pin PB2
#define TEMPERATURE_PRECISION 12

#define SOIL_MOIST_1  PA0
#define SOIL_MOIST_2  PA1
#define SOIL_MOIST_3  PA2

#define GREEN_LED     PA5
#define RED_LED       PA9

/* SPARKFUN MOISTURE SENSOR SPECIFIC */
#define SPARKFUN_MOIST_ADDR_1   0x29
#define SPARKFUN_MOIST_ADDR_2   0x28
#define COMMAND_LED_OFF       0x00
#define COMMAND_LED_ON        0x01
#define COMMAND_GET_VALUE     0x05
#define COMMAND_NOTHING_NEW   0x99

/* Index Tracker */
uint64_t idx_tracker = 0;

/* SPARKFUN SI7021 SPECIFIC */
//Create Instance of HTU21D or SI7021 temp and humidity sensor and MPL3115A2 barrometric sensor
//Weather si7021;
//float humidity = 0;
//float tempf = 0;
Adafruit_Si7021 si7021 = Adafruit_Si7021();
bool enableHeater = false;
uint8_t loopCnt = 0;


/* SCD30 SPECIFIC */
SCD30 airSensor;
uint8_t sensorState = 0;

/* BME680 SPECIFIC */
BME680_Class BME680; ///< Create an instance of the BME680 class
static int32_t  BME_temp, BME_humidity, BME_pressure, BME_gas;    // Variable to store readings
static float    alt;   // temp variable for altitude
float altitude(const int32_t press, const float seaLevel = 1013.25); ///< Forward function declaration with default value for sea level
float altitude(const int32_t press, const float seaLevel) 
{
  /*!
  * @brief     This converts a pressure measurement into a height in meters
  * @details   The corrected sea-level pressure can be passed into the function if it is know, otherwise the standard 
  *            atmospheric pressure of 1013.25hPa is used (see https://en.wikipedia.org/wiki/Atmospheric_pressure)
  * @param[in] press    Pressure reading from BME680
  * @param[in] seaLevel Sea-Level pressure in millibars
  * @return    floating point altitude in meters.
  */
  static float Altitude;
  Altitude = 44330.0*(1.0-pow(((float)press/100.0)/seaLevel,0.1903)); // Convert into altitude in meters
  return(Altitude);
} // of method altitude()

/* Moisture Sensor Specific */
uint16_t soilMoisture_1, soilMoisture_2, soilMoisture_3;


// Setup a oneWire instance to communicate with any OneWire devices (not just Maxim/Dallas temperature ICs)
OneWire oneWire(TEMP);

// Pass our oneWire reference to Dallas Temperature.
DallasTemperature sensors(&oneWire);

DeviceAddress TEMP_0   = { 0x28, 0x97, 0xE3, 0x36, 0x91, 0x10, 0x02, 0x89 };
DeviceAddress TEMP_1   = { 0x28, 0x87, 0x83, 0x77, 0x91, 0x10, 0x02, 0x09 };
DeviceAddress TEMP_2   = { 0x28, 0xAB, 0x06, 0x77, 0x91, 0x0A, 0x02, 0xD0 };
DeviceAddress TEMP_3   = { 0x28, 0x93, 0xDD, 0x77, 0x91, 0x09, 0x02, 0xE7 };
DeviceAddress TEMP_4   = { 0x28, 0x1F, 0xA6, 0x77, 0x91, 0x08, 0x02, 0xA9 };

/* *********************************************************************** */
/*                DATA PACKET SETUP               */
/* *********************************************************************** */
StaticJsonDocument<400> doc;


auto timer = timer_create_default(); // create a timer with default settings
uint8_t led_state = 0;


bool sampleSensors(void *) {

  doc["start_time"] = millis();
  doc["idx"] = idx_tracker;
  idx_tracker += 1;
  
//  digitalWrite(GREEN_LED, !digitalRead(GREEN_LED));
//  led_state = !led_state;
//  if(led_state){
//    greenLED_on(); //on
//  }else{
//    greenLED_off(); //off
//  }
  greenLED_on();
  
//  delayMicroseconds(1000000);
//  digitalWrite(GREEN_LED, LOW);
//  digitalWrite(RED_LED, HIGH);
//  delayMicroseconds(1000000);

  sensors.requestTemperatures();
  doc["temp_0"] = getTemperature(TEMP_0);
  doc["temp_1"] = getTemperature(TEMP_1);
  doc["temp_2"] = getTemperature(TEMP_2);
  doc["temp_3"] = getTemperature(TEMP_3);
  doc["temp_4"] = getTemperature(TEMP_4);

  doc["SF_moist_1"] = sparkfun_moist_get_value(SPARKFUN_MOIST_ADDR_1);
  doc["SF_moist_2"] = sparkfun_moist_get_value(SPARKFUN_MOIST_ADDR_2);

  /* SAMPLE CO2 SENSOR */
  sampleAirQuality();

  /* SAMPLE BME680 SENSOR */
  BME680.getSensorData(BME_temp,BME_humidity,BME_pressure,BME_gas);  // Get the most recent readings
  BME_sampleConversion();
  

  /* SI7021 */
  doc["si7021"]["temp"] = si7021.readHumidity();
  doc["si7021"]["hum"] = si7021.readTemperature();

  // Toggle heater enabled state every 10 minutes if humidity reading over 80
  // An ~1.8 degC temperature increase can be noted when heater is enabled
  if(doc["si7021"]["hum"] > 80){
    loopCnt += 1;

    if((!enableHeater) && loopCnt > 600){ //turn on heater if higher humidity measurements read for 10 minutes
      enableHeater = true;
      doc["si7021"]["heater"] = enableHeater;
  
      si7021.heater(enableHeater);
      loopCnt = 0;
    }else-if(enableHeater && (loopCnt > 30)){ // turn off after 30 seconds
      enableHeater = false;
      doc["si7021"]["heater"] = enableHeater;
  
      si7021.heater(enableHeater);
      loopCnt = 0;
    }
    
  }else-if(loopCnt != 0){ // if heater is on and humidity dropped below 80, keep on for full 30 second interval
    loopCnt += 1;
    if(enableHeater && (loopCnt > 30)){ // turn off after 30 seconds
      enableHeater = false;
      doc["si7021"]["heater"] = enableHeater;
  
      si7021.heater(enableHeater);
      loopCnt = 0;
    }
  }

  /* Sample Soil Moisture Sensors */
  soilMoisture_1 = analogRead(SOIL_MOIST_1);
  soilMoisture_2 = analogRead(SOIL_MOIST_2);
  soilMoisture_3 = analogRead(SOIL_MOIST_3);

  doc["soil_m_1"] = soilMoisture_1;
  doc["soil_m_2"] = soilMoisture_2;
  doc["soil_m_3"] = soilMoisture_3;

//  serializeJsonPretty(doc, Serial);
  serializeJson(doc, Serial);
  Serial.println();
  
  greenLED_off();
  
  return true; // repeat? true
}


void setup() {
  
  // put your setup code here, to run once:
  digitalWrite(RED_LED, HIGH);
  pinMode(GREEN_LED, OUTPUT_OPEN_DRAIN); //http://docs.leaflabs.com/static.leaflabs.com/pub/leaflabs/maple-docs/0.0.12/lang/api/pinmode.html
  pinMode(RED_LED, OUTPUT_OPEN_DRAIN); //http://docs.leaflabs.com/static.leaflabs.com/pub/leaflabs/maple-docs/0.0.12/lang/api/pinmode.html

  Serial.begin(115200);

  delay(5);

  Wire.setSDA(PB9);
  Wire.setSCL(PB8);
  Wire.begin();
  

  /* *********************************************************************** */
  /*                TEMPERATURE SENSORS               */
  /* *********************************************************************** */
    // Start up the library
  sensors.begin();

  // locate devices on the bus
  Serial.print("Locating devices...");
  Serial.print("Found ");
  Serial.print(sensors.getDeviceCount(), DEC);
  Serial.println(" devices.");

  // report parasite power requirements
  Serial.print("Parasite power is: ");
  if (sensors.isParasitePowerMode()) Serial.println("ON");
  else Serial.println("OFF");

  // Search for devices on the bus and assign based on an index. Ideally,
  // you would do this to initially discover addresses on the bus and then
  // use those addresses and manually assign them (see above) once you know
  // the devices on your bus (and assuming they don't change).
  //
  // method 1: by index
  if (!sensors.getAddress(TEMP_0, 0)) Serial.println("Unable to find address for Device 0");
  if (!sensors.getAddress(TEMP_1, 1)) Serial.println("Unable to find address for Device 1");
  if (!sensors.getAddress(TEMP_2, 2)) Serial.println("Unable to find address for Device 2");
  if (!sensors.getAddress(TEMP_3, 3)) Serial.println("Unable to find address for Device 3");
  if (!sensors.getAddress(TEMP_4, 4)) Serial.println("Unable to find address for Device 4");

  // set the resolution to 9 bit per device
  sensors.setResolution(TEMP_0, TEMPERATURE_PRECISION);
  sensors.setResolution(TEMP_1, TEMPERATURE_PRECISION);
  sensors.setResolution(TEMP_2, TEMPERATURE_PRECISION);
  sensors.setResolution(TEMP_3, TEMPERATURE_PRECISION);
  sensors.setResolution(TEMP_4, TEMPERATURE_PRECISION);

  /* *********************************************************************** */
  /*                SI7021 SENSOR               */
  /* *********************************************************************** */
  if (!si7021.begin()) {
    Serial.println("Did not find Si7021 sensor!");
    while (true)
    ;
  }
  doc["si7021"]["heater"] = enableHeater;


  /* *********************************************************************** */
  /*                SCD30 SENSOR               */
  /* *********************************************************************** */
  if (airSensor.begin() == false)
  {
    Serial.println("Air sensor not detected. Please check wiring. Freezing...");
    while (1)
      ;
  }

  /* *********************************************************************** */
  /*                BME680 SENSOR               */
  /* *********************************************************************** */
  while (!BME680.begin(I2C_STANDARD_MODE)) // Start BME680 using I2C protocol
  {
    Serial.print(F("-  Unable to find BME680. Trying again in 5 seconds.\n"));
    delay(5000);
  } // of loop until device is located
  //  Serial.print(F("- Setting 16x oversampling for all sensors\n"));
  BME680.setOversampling(TemperatureSensor,Oversample16); // Use enumerated type values
  BME680.setOversampling(HumiditySensor,   Oversample16); // Use enumerated type values
  BME680.setOversampling(PressureSensor,   Oversample16); // Use enumerated type values
  //  Serial.print(F("- Setting IIR filter to a value of 4 samples\n"));
  BME680.setIIRFilter(IIR4); // Use enumerated type values
  //  Serial.print(F("- Setting gas measurement to 320\xC2\xB0\x43 for 150ms\n")); // "�C" symbols
  BME680.setGas(320,150); // 320�c for 150 milliseconds

  
  // call the sampler function every 5000 millis (5 second)
  timer.every(5000, sampleSensors);

}

//------------------------------------------------------------------------------
// WARNING idle loop has a very small stack (configMINIMAL_STACK_SIZE)
// loop must never block
void loop() {

  timer.tick(); // tick the timer

}


void BME_sampleConversion(){
//  Serial.print( ( (float) BME_temp)/100);
//  Serial.print(",");



//  Serial.print( ( (float) BME_humidity)/1000);
//    Serial.print(",");
//
//  Serial.print( ( (float) BME_pressure)/100);
//    Serial.print(",");
//
//  alt = altitude(BME_pressure);                                                         // temp variable for altitude
//  Serial.print( ( (float) alt));
//    Serial.print(",");
//
//  Serial.print( ( (float) BME_gas)/100);
//  Serial.println();

  doc["BME680"]["temp"] = ( (float) BME_temp)/100;
  doc["BME680"]["hum"] = ( (float) BME_humidity)/1000;
  doc["BME680"]["pres"] = ( (float) BME_pressure)/100;
  doc["BME680"]["gas"] = ( (float) BME_gas)/100;
}

void sampleAirQuality(){
    while(sensorState == 0){
    if(airSensor.dataAvailable())
    {
      sensorState = 1;
//      //Serial.print("co2(ppm):");
//        Serial.print(",");
//      Serial.print(airSensor.getCO2());
//  
//      //Serial.print(" temp(C):");
//        Serial.print(",");
//      Serial.print(airSensor.getTemperature(), 1);
//  
//      //Serial.print(" humidity(%):");
//        Serial.print(",");
//      Serial.print(airSensor.getHumidity(), 1);
//  
//      Serial.println();
      
      doc["SCD30"]["CO2"] = airSensor.getCO2();
      doc["SCD30"]["temp"] = airSensor.getTemperature();
      doc["SCD30"]["hum"] = airSensor.getHumidity();
    }
  }
  sensorState = 0;

}


void greenLED_on(){
  analogWrite(GREEN_LED, 240);
}

void greenLED_off(){
  analogWrite(GREEN_LED, 255);
}

void redLED_on(){
  analogWrite(RED_LED, 240);
}

void redLED_off(){
  analogWrite(RED_LED, 255);
}

// function to print the temperature for a device
float getTemperature(DeviceAddress deviceAddress)
{
  float tempC = sensors.getTempC(deviceAddress);
  if(tempC == DEVICE_DISCONNECTED_C) 
  {
    int retry_attempts = 5;
    while(retry_attempts >= 0){
      float tempC = sensors.getTempC(deviceAddress);
      if(tempC == DEVICE_DISCONNECTED_C){
        retry_attempts -= 1;
      }else{
        retry_attempts = -1;
      }
    }
    if(retry_attempts == 0){
      Serial.println("Error: Could not read temperature data");
      return -1000;
    }
  }

//  Serial.print("Temp C: ");
//  Serial.print(tempC);
//  Serial.print(" Temp F: ");
//  Serial.print(DallasTemperature::toFahrenheit(tempC));
//  Serial.println();

  return tempC;

}



/******** SPARKFUN MOISTURE SENSOR FUNCTIONS ************/

uint16_t sparkfun_moist_get_value(uint8_t address) {
  uint16_t ADC_VALUE;
  Wire.beginTransmission(address);
  Wire.write(COMMAND_GET_VALUE); // command for status
  Wire.endTransmission();    // stop transmitting //this looks like it was essential.

  Wire.requestFrom(address, 2);    // request 1 bytes from slave device qwiicAddress

  while (Wire.available()) { // slave may send less than requested  (PC: this seems hacky, SparkFun.... )
  uint8_t ADC_VALUE_L = Wire.read(); 
  uint8_t ADC_VALUE_H = Wire.read();

  ADC_VALUE=ADC_VALUE_H;
  ADC_VALUE<<=8;
  ADC_VALUE|=ADC_VALUE_L;
//  Serial.print("ADC_VALUE:  ");
//  Serial.println(ADC_VALUE,DEC);
  }
  uint16_t x=Wire.read();  //PC: why is this here?

  return ADC_VALUE;
}

void sparkfun_moisture_ledOn(uint8_t address) {
  Wire.beginTransmission(address);
  Wire.write(COMMAND_LED_ON);
  Wire.endTransmission();
}

void sparkfun_moisture_ledOff(uint8_t address) {
  Wire.beginTransmission(address);
  Wire.write(COMMAND_LED_OFF);
  Wire.endTransmission();
}
