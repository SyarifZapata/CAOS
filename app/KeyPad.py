from nanpy import (ArduinoApi, SerialManager)
from time import sleep
import RPi.GPIO as GPIO
from RPLCD import CharLCD

GPIO.setmode(GPIO.BCM)
DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)



try:
    connection = SerialManager()
    a = ArduinoApi(connection = connection)

except:
    print("Failed to connect to Arduino")

# Setup the pinModes as if we were in the Arduino IDE



#Setup keypad

MATRIX = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']]

COL = [5, 4, 3, 2]
ROW = [9, 8, 7, 6]



for j in range(4):
    a.pinMode(COL[j], a.OUTPUT)
    a.digitalWrite(COL[j], a.HIGH)

for i in range(4):
    a.pinMode(ROW[i], a.INPUT)
    a.digitalWrite(ROW[i], a.INPUT_PULLUP)

cursorPosition = 0

password = ['1', '2', '3', '4']

userInput = []

check = ""

def checkPassword(input):
    
    if input == password:
        lcd.clear()
        lcd.write_string(u'Access granted')
        lcd.cursor_pos = (1,0)
        lcd.write_string(u'****************')
        check = "success"
    else:
        lcd.clear()
        lcd.write_string(u'Access denied')
        lcd.cursor_pos = (1, 0)
        lcd.write_string(u'Wrong Password')
        sleep(2)
        lcd.clear()
        check = "failed"
    
try:
    while(True):
        for j in range(4):
            a.digitalWrite(COL[j], a.LOW)

            for i in range(4):
                
                if a.digitalRead(ROW[i]) == a.LOW:
                    
                   pressedButton = MATRIX[i][j]
                   if pressedButton == '#':
                       checkPassword(userInput)
                       if check == "success":
                           break
                       else:
                           userInput = []
                           cursorPosition = 0
                   else:
                       userInput.append(pressedButton)
                       print (pressedButton)
                       print (i)
                       print (j)
                       lcd.cursor_pos = (0, cursorPosition)
                       lcd.write_string(u'%c' % pressedButton)
                       cursorPosition += 1
                while(a.digitalRead(ROW[i]) == a.LOW):
                        pass                          #do nothing as long button still pressed
            a.digitalWrite(COL[j], a.HIGH)    
                         

except KeyboardInterrupt:
    lcd.clear()