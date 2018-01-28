from socketIO_client_nexus import SocketIO
from nanpy import (ArduinoApi, SerialManager)
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
from time import sleep
import time
import cv2
import numpy as np
#from RPLCD import CharLCD
from Adafruit_CharLCD import Adafruit_CharLCD
from threading import Thread
import pygame

#init sound
pygame.mixer.init()

#Setup Pin
GPIO.setmode(GPIO.BCM)
LEDPin = 22
LEDPinRot = 17
motionDetector = 21
GPIO.setup(LEDPin, GPIO.OUT)
GPIO.setup(LEDPinRot, GPIO.OUT)
GPIO.setup(motionDetector, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#Message Controller
message1 = False
message2 = False
message3 = False

#Setup keypad. Represents a 4x4 matrix with its entries.
MATRIX = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']]

#The pin numbers for column and rows.
COL = [5, 4, 3, 2]
ROW = [9, 8, 7, 6]

#LCD set up of its pin numbers.
DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

#initializes lcd with the according pin numbers.
lcd = Adafruit_CharLCD(rs=PinRS, en=PinE, d4=DataPin_4, d5=DataPin_5, d6=DataPin_6, d7= DataPin_7, cols = 16, lines=2)

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("recognizer/trainingData.yml")
id = 0
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
fontColor = (255, 255, 255)
ledCounter = 0

startTimeFaceDetected = 0
startTimeNoFaceDetected = 0
faceDetected = False

#Tries establishing connection to the Arduino via serial port.
try:
    connecter = SerialManager()
    #Instance of ArduinoApi object.
    arduino = ArduinoApi(connection = connecter)
except:
    print("cannot connect to Arduino")
    

#Setup Keypad
#Setup column pins as outputs and set high.
for j in range(4):
    arduino.pinMode(COL[j], arduino.OUTPUT)
    arduino.digitalWrite(COL[j], arduino.HIGH)

#Setup row pins as inputs with pull-up resistors.
for i in range(4):
    arduino.pinMode(ROW[i], arduino.INPUT)
    arduino.digitalWrite(ROW[i], arduino.INPUT_PULLUP)

cursorPosition = 0
password = ['1', '2', '3', '4']
userInput = []
check = ""
beforeFirstButtonPressed = True
tooManyButtonsPressed = False
waitingForAccess = False
passwordCounter = 0
attempts = 3
accessBlocked = False


#Checks password that is entered via keypad.
def checkPassword(input):

    global check
    global passwordCounter
    global attempts
    global accessBlocked
    global lastAccessBlocked
    global waitingForAccess

    if input == password:
        if(not accessBlocked):                                  #when password is correct and access is not blocked, then access will be granted.
            lcd.clear()
            lcd.message(u'Access granted')
            lcd.set_cursor(0,1)
            lcd.message(u'****************')
            sleep(2)
            lcd.clear()
            check = "success"
        else:                                                   #When password is correct but access is still blocked, then access will be denied.
            lcd.clear()
            lcd.message(u'Access denied')
            lcd.set_cursor(0,1)
            lcd.message(u'Wrong Password')
            sleep(2)
            lcd.clear()
            check = "failed"
            waitingForAccess = True
            
    else:
        if(not accessBlocked):                                  #when password is incorrect and access is not blocked, then access will be denied.
            lcd.clear()
            lcd.message(u'Access denied')
            lcd.set_cursor(0,1)
            lcd.message(u'Wrong Password')
            sleep(2)
            lcd.clear()
            passwordCounter += 1
            remainingAttempts = attempts - passwordCounter
            if passwordCounter == attempts:                         #if password is already entered wrong three times, then access will be blocked for 30s.
                lcd.message("Please try\nagain in 30s!")
                sleep(2)
                lcd.clear()
                accessBlocked = True
                lastAccessBlocked = current_milis()
                waitingForAccess = True
            else:
                lcd.message("You have %(remainingAttempts)d remai\nning attempts" % {"remainingAttempts": remainingAttempts})
                sleep(2)
                lcd.clear()
            check = "failed"
        else:                                                       #when password is wrong and access is blocked, then access will be denied.
            lcd.clear()
            lcd.message(u'Access denied')
            lcd.set_cursor(0,1)
            lcd.message(u'Wrong Password')
            sleep(2)
            lcd.clear()
            waitingForAccess = True
        

def current_milis():
    return int(round(time.time()))

lastAccessBlocked = current_milis()

def on_disconnect():
    print('disconnect')
    
def on_connect(*args):
    print("connected to Server")
    socketIO.emit('clientPi',"Pi: I'm now connected to the server")
    
def on_buzzer(*args):
    if(args[0]['message'] == "relayON"):
        pygame.mixer.music.load("buzzer.mp3")
        pygame.mixer.music.play()
    
def threaded_function(arg):
    socketIO.wait()
    

socketIO = SocketIO('139.162.182.153',3008)
socketIO.on('welcome', on_connect)
socketIO.on('disconnect',on_disconnect)
socketIO.on('arduino',on_buzzer)
thread = Thread(target = threaded_function, args = (10, ))
thread.start()

try:
    GPIO.output(LEDPin, False)
    while True:
        startTimeNoFaceDetected = current_milis()
        if(faceDetected):
            lcd.clear()
            lcd.message("Enter Password:")
            #this while loop handles the whole process of checking the password through the keypad.
            while(True):
                         #condition to break out of the while loop when access is granted and the system should go back to the motion detector.
                        if(faceDetected == False):
                            break
                        #Sets outputs of column low one at a time.
                        for j in range(4):
                            arduino.digitalWrite(COL[j], arduino.LOW)
                            #condition to break out of the for loop when access is granted and the system should go back to the motion detector.
                            if(faceDetected == False):
                                break
                            #checks each row pin if it is set low. If so then this row pin is pressed.
                            for i in range(4):
                                if arduino.digitalRead(ROW[i]) == arduino.LOW:  #checks if button is pressed.
                                   pressedButton = MATRIX[i][j]
                                   #check if pressed button has space on the first line of the LCD.
                                   if cursorPosition < 16:
                                           #Button "D" is for ending the process of entering a password. This will be used for admin if he wants to open the door by the app.
                                           if pressedButton == 'D':
                                               faceDetected = False
                                               break
                                           #Button "#" is for confirming the password. Checks automatically the confirmed password.
                                           if pressedButton == '#':
                                               checkPassword(userInput)
                                               #If access is granted then activate relais (open door) and break out of the while loop.
                                               if check == "success":
                                                   faceDetected = False
                                                   socketIO.emit('clientPi',"faceDetected")
##                                                   pygame.mixer.music.load("buzzer.mp3")
##                                                   pygame.mixer.music.play()
                                                   
                                                   GPIO.output(LEDPin, False)
                                                   break
                                               #If password is incorrect reset entered buttons and count attempts.
                                               else:
                                                   userInput = []
                                                   cursorPosition = 0
                                                   if passwordCounter == attempts:
                                                       faceDetected = False
                                                       break

                                           else:
                                               #this condition is true if the keypad is pressed for the first time or too many
                                               #characters are typed in.                                    
                                               if (beforeFirstButtonPressed or tooManyButtonsPressed):
                                                   lcd.clear()
                                                   tooManyButtonsPressed = False
                                                #this condition is true if any password is entered while access is blocked
                                               if (waitingForAccess):
                                                   lcd.clear()
                                                   print("sssss")
                                                   waitingForAccess = False
                                               userInput.append(pressedButton)
                                               #print pressedButton             ;prints out the pressed button and its column and row number.
                                               #print i
                                               #print j
                                               lcd.set_cursor(cursorPosition,0)
                                               lcd.message("*")
                                               beforeFirstButtonPressed = False
                                               cursorPosition += 1
                                   #When LCD's first line is already full then delete LCD and reset all pressed buttons.
                                   else:
                                       lcd.clear()
                                       lcd.set_cursor(0, 0)
                                       lcd.message(u'Too many Buttons')
                                       lcd.set_cursor(0,1)
                                       lcd.message(u' were pressed!')
                                       sleep(2)
                                       lcd.clear()
                                       userInput = []
                                       lcd.message("Enter Password\nagain")
                                       tooManyButtonsPressed = True
                                       cursorPosition = 0
                                #do nothing as long same button is still pressed.
                                while(arduino.digitalRead(ROW[i]) == arduino.LOW):
                                    pass
                            arduino.digitalWrite(COL[j], arduino.HIGH)      #Sets column pin number back to high after checking.
            
        if(GPIO.input(motionDetector)):

            message1 = False
            message2 = False
            message3 = False
            socketIO.emit('clientPi',"Pi: Someone is there")
            strangerDetected = False
            inCall = False
            #message when camera is turned off
            lcd.clear()
            lcd.message('Welcome to CAOS\nSecurity System')
            print("motion detected")    #Breakpoint
            #lcd.write_string(u'Welcome! Please\n\rlook to the cam')
        
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceDetect.detectMultiScale(gray, 1.3, 5)
                if(current_milis()-lastAccessBlocked >= 30):
                    accessBlocked = False
                    passwordCounter = 0
                    
                    
                if(not message1):
                    lcd.clear()
                    lcd.message("   Do not move\n Detecting face")
                    message1 = True
                
                if (ledCounter > 10):
                    GPIO.output(LEDPin, False)
                    GPIO.output(LEDPinRot, False)
                    
                inputValue = GPIO.input(16)
                if(inputValue == False):
                    pygame.mixer.music.load("bell.mp3")
                    pygame.mixer.music.play()
##                    while pygame.mixer.music.get_busy() == True:
##                        continue
                    
                if(inputValue == False and strangerDetected):
                    print("Button Pressed") #Breakpoint
                    lcd.clear()
                    if(not inCall):
                        socketIO.emit('clientPi',"strangerDetected")
                        inCall = True
                        lcd.message("Process Calling\nPlease Wait. . .")
                        sleep(4)
                        lcd.clear()
                    
                
                for (x,y,w,h) in faces:
                    startTimeNoFaceDetected = current_milis()
                    cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                    id, conf = rec.predict(gray[y:y+h, x:x+w])
                    confStr = "{0:.2f}".format(100-conf)
                    
                    if(inputValue == False):
                        pygame.mixer.music.load("bell.mp3")
                        pygame.mixer.music.play()
##                        while pygame.mixer.music.get_busy() == True:
##                            continue
                    
                    #button activated
                    if(inputValue == False and strangerDetected):
                        print("Button Pressed")
                        lcd.clear()
                        if(not inCall):
                            socketIO.emit('clientPi',"strangerDetected")
                            inCall = True
                            lcd.message("Process Calling\nPlease Wait. . .")
                            sleep(4)
                            lcd.clear()
                            

                    if(id==1):
                        id = "Syarif"
                        ledCounter = 0
                    elif(id==2):
                        id = "Alice"
                    elif(id==3):
                        id="Simon"   

                    if conf<50:
                        cv2.putText(img, str(id), (x, y + h), font, fontScale, fontColor)
                        GPIO.output(LEDPin, True)
                        print("GREEN LED IS ON")
                        GPIO.output(LEDPinRot, False)
                        if(not message2):
                            lcd.clear()
                            lcd.message("Face Detected!")
                            sleep(2)
                            lcd.clear()
                            lcd.message("Welcome %s!" % (id))
                            lcd.set_cursor(0,1)
                            message2 = True
                            
                        faceDetected = True
                        break
                        

                    elif conf>80:
                        cv2.putText(img, "Warning, Stranger!", (x, y + h), font, fontScale, (0, 0, 255))
                        GPIO.output(LEDPinRot, True)
                        GPIO.output(LEDPin, False)
                        if(not message3):
                            lcd.clear()
                            lcd.message("Face ")
                            lcd.set_cursor(0,1)
                            lcd.message("Not Detected")
                            sleep(2)
                            lcd.clear()
                            lcd.message("Welcome Stranger")
                            sleep(2)
                            lcd.clear()
                            lcd.message("Please \nPush the Button")
                            message3 = True

                        
                        if(not strangerDetected):
                            strangerDetected = True
                    else:
                        cv2.putText(img, str(confStr)+ "%", (x, y + h), font, fontScale, fontColor)

                
                    
                ledCounter += 1
                cv2.imshow('name',img)
                rawCapture.truncate(0)
                
                if(faceDetected):
                    print("fertig lustig")  #Breakpoint
                    break
                
                #exit if you press q
                if(current_milis()-startTimeNoFaceDetected > 20):
                    lcd.clear()
                    break
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print(startTimeNoFaceDetected)
                    print(current_milis())
                    break
                    
            
            cv2.destroyAllWindows()
            
except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print("exit by user") 
            
finally:
	GPIO.cleanup()
	
