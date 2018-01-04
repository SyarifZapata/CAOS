import pyfirmata
from RPLCD import CharLCD
import RPi.GPIO as GPIO

board = pyfirmata.Arduino('/dev/ttyACM0')

GPIO.setmode(GPIO.BCM)

DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)


#RST_PIN = board.get_pin('d:9:o')
#SS_PIN = board.get_pin('d:10:o')


#readCard[4]
#myTags[100] = {}
tagsCount = 0
tagID = ""
successRead = False
correctTag = False


lcd.write_string('Hello Simon')
