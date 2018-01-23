from Adafruit_CharLCD import Adafruit_CharLCD
from time import sleep

DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

lcd = Adafruit_CharLCD(rs=PinRS, en=PinE, d4=DataPin_4, d5=DataPin_5, d6=DataPin_6, d7= DataPin_7, cols = 16, lines=2)
lcd.clear()

# display text on LCD display \n = new line
lcd.message('Adafruit CharLCD\n  Raspberry Pi')
sleep(3)

# scroll text off display
for x in range(0, 16):
    lcd.move_right()
    sleep(.1)
sleep(3)
# scroll text on display
for x in range(0, 16):
    lcd.move_left()
    sleep(.1)