from nanpy import (ArduinoApi, SerialManager)
from time import sleep
import RPi.GPIO as GPIO
from RPLCD import CharLCD

GPIO.setmode(GPIO.BCM)

# Set up LCD 
DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)


# Connect Arduino with Raspberry Pi
try:
    connecter = SerialManager()
    arduino = ArduinoApi(connection = connecter)

except:
    print("Failed to connect to Arduino")



#Setup keypad

MATRIX = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']]

COL = [5, 4, 3, 2]
ROW = [9, 8, 7, 6]



for j in range(4):
    arduino.pinMode(COL[j], arduino.OUTPUT)
    arduino.digitalWrite(COL[j], arduino.HIGH)

for i in range(4):
    arduino.pinMode(ROW[i], arduino.INPUT)
    arduino.digitalWrite(ROW[i], arduino.INPUT_PULLUP)

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
        sleep(2)
        lcd.clear()
        check = "success"
    else:
        lcd.clear()
        lcd.write_string(u'Access denied')
        lcd.cursor_pos = (1, 0)
        lcd.write_string(u'Wrong Password')
        sleep(2)
        lcd.clear()
        check = "failed"
        
# Instruction message      
lcd.cursor_pos = (0, 0)
lcd.write_string(u'Enter Password')
lcd.cursor_pos = (1, 0)
lcd.write_string(u'Confirm with *')
sleep(4)
lcd.clear()

try:
    while(True):
        for j in range(4):
            arduino.digitalWrite(COL[j], arduino.LOW)
            for i in range(4):
                if arduino.digitalRead(ROW[i]) == arduino.LOW:  #check if button is pressed
                   pressedButton = MATRIX[i][j]
                   if cursorPosition < 16:
	                   if pressedButton == '#':
	                       checkPassword(userInput)
	                       if check == "success":
	                           break
	                       else:
	                           userInput = []
	                           cursorPosition = 0
	                   else:
	                       userInput.append(pressedButton)
	                       #print pressedButton
	                       #print i
	                       #print j
	                       lcd.cursor_pos = (0, cursorPosition)
	                       lcd.write_string(u'%c' % pressedButton)
	                       cursorPosition += 1
	           else:
	               lcd.clear()
	               lcd.cursor_pos = (0, 0)
		       lcd.write_string(u'Too many Buttons')
		       lcd.cursor_pos = (1, 0)
		       lcd.write_string(u' were pressed!')
		       sleep(2)
		       lcd.clear()
		       cursorPosition = 0
                while(arduino.digitalRead(ROW[i]) == arduino.LOW):
                    pass                                          #do nothing as long button still pressed
            arduino.digitalWrite(COL[j], arduino.HIGH)    
                         

except KeyboardInterrupt:
    lcd.clear()
    GPIO.cleanup()
    print ("KeyboardInterrupt")
    
except ValueError:
    lcd.clear()
    GPIO.cleanup()
    print ("Value Error")