from RPLCD import CharLCD
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)

counter = 0

while counter != 8:
    lcd.cursor_pos=(0,3)
    lcd.write_string(u'Calling ')
    lcd.cursor_pos=(1,3)
    lcd.write_string(u'Mr. Kwik...')
    time.sleep(1)
    lcd.clear()
    lcd.write_string(u'Please wait...')
    time.sleep(1)
    lcd.clear()
    time.sleep(0.4)
    counter = counter + 1

print(counter)
