from nanpy import (ArduinoApi, SerialManager)
from RPLCD import CharLCD
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)



ledPin = 13

try:
    connecter = SerialManager()
    arduino = ArduinoApi(connection = connecter)
except:
    print("Failed to connect to Arduino")
    
# Set up the pin modes as  if we were in Arduino IDE
arduino.pinMode(ledPin, arduino.OUTPUT)
