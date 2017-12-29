import pyfirmata
from RPLCD import CharLCD

board = pyfirmata.Arduino('/dev/ttyACM0')

DataPin_4 = board.get_pin('d:4:o')
DataPin_5 = board.get_pin('d:5:o')
DataPin_6 = board.get_pin('d:6:o')
DataPin_7 = board.get_pin('d:7:o')
PinRS = board.get_oin('d:2:o')
PinE = board.get_pin('d:3:o')

lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)

RST_PIN = board.get_pin('d:9:o')
SS_PIN = board.get_pin('d:10:o')


readCard[4]
myTags[100] = {}
tagsCount = 0
tagID = ""
successRead = false
correctTag = false
