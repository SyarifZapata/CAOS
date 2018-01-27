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

#Setup keypad
MATRIX = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']]

COL = [5, 4, 3, 2]
ROW = [9, 8, 7, 6]

#LCD set up
DataPin_4 = 5
DataPin_5 = 6
DataPin_6 = 13
DataPin_7 = 19
PinRS = 18
PinE = 23

#lcd = CharLCD(cols=16, rows=2, pin_rs=PinRS, pin_e=PinE, pins_data=[DataPin_4, DataPin_5, DataPin_6, DataPin_7], numbering_mode = GPIO.BCM)
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

try:
    connecter = SerialManager()
    arduino = ArduinoApi(connection = connecter)
except:
    print("cannot connect to Arduino")
    

#Setup Keypad
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
beforeFirstButtonPressed = True
tooManyButtonsPressed = False
passwordCounter = 0
attempts = 3
accessBlocked = False


#Check password for keypad
def checkPassword(input):
    global check
    global passwordCounter
    global attempts
    global accessBlocked
    global lastAccessBlocked
    if input == password:
        if(not accessBlocked):
            lcd.clear()
            lcd.message(u'Access granted')
            lcd.set_cursor(0,1)
            lcd.message(u'****************')
            sleep(2)
            lcd.clear()
            check = "success"
        else:
            lcd.clear()
            lcd.message(u'Access denied')
            lcd.set_cursor(0,1)
            lcd.message(u'Wrong Password')
            sleep(2)
            lcd.clear()
            check = "failed"
            
    else:
        if(not accessBlocked):
            lcd.clear()
            lcd.message(u'Access denied')
            lcd.set_cursor(0,1)
            lcd.message(u'Wrong Password')
            sleep(2)
            lcd.clear()
            passwordCounter += 1
            remainingAttempts = attempts - passwordCounter
            if passwordCounter == attempts:
                lcd.message("Please try\nagain in 30s")
                sleep(2)
                lcd.clear()
                accessBlocked = True
                lastAccessBlocked = current_milis()
                print(lastAccessBlocked)
            else:
                lcd.message("You have %(remainingAttempts)d \nremaining attempts" % {"remainingAttempts": remainingAttempts})
                sleep(2)
                lcd.clear()
            check = "failed"
        else:
            lcd.clear()
            lcd.message(u'Access denied')
            lcd.set_cursor(0,1)
            lcd.message(u'Wrong Password')
            sleep(2)
            lcd.clear()
        

def current_milis():
    return int(round(time.time()))

lastAccessBlocked = current_milis()

def on_disconnect():
    print('disconnect')
    
def on_connect(*args):
    print("connected to Server")
    socketIO.emit('clientPi',"Pi: I'm now connected to the server")

socketIO = SocketIO('139.162.182.153',3008)
socketIO.on('welcome', on_connect)
socketIO.on('disconnect',on_disconnect)

try:
    
    while True:
        startTimeNoFaceDetected = current_milis()
        if(faceDetected):
            lcd.clear()
            lcd.message("Enter Password:")
            while(True):
                        #print("immer no ih de while schlaufe")  #Breakpoint to know where we are
                        if(faceDetected == False):
                            print("aussen") #Breakpoint
                            break
                        for j in range(4):
                            arduino.digitalWrite(COL[j], arduino.LOW)
                            if(faceDetected == False):
                                print("innen")  #Breakpoint
                                break
                            for i in range(4):
                                if arduino.digitalRead(ROW[i]) == arduino.LOW:  #check if button is pressed
                                   pressedButton = MATRIX[i][j]
                                   if cursorPosition < 16:
                                           if pressedButton == '#':
                                               checkPassword(userInput)
                                               if check == "success":
                                                   faceDetected = False
                                                   socketIO.emit('clientPi',"faceDetected")                                                   
                                                   break
                                               else:
                                                   #print("Mann simon")  #Breakpoint
                                                   userInput = []
                                                   cursorPosition = 0
                                                   if passwordCounter == attempts:
                                                       faceDetected = False
                                                       break
                                                       
                                                   
                                           else:
                                               if (beforeFirstButtonPressed or tooManyButtonsPressed):
                                                   lcd.clear()
                                                   tooManyButtonsPressed = False
                                               userInput.append(pressedButton)
                                               #print pressedButton
                                               #print i
                                               #print j
                                               lcd.set_cursor(cursorPosition,0)
                                               lcd.message("*")
                                               #lcd.message(u'%c' % pressedButton)
                                               beforeFirstButtonPressed = False
                                               cursorPosition += 1
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
                                while(arduino.digitalRead(ROW[i]) == arduino.LOW):
                                    pass                                          #do nothing as long button still pressed
                            arduino.digitalWrite(COL[j], arduino.HIGH)
            
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
                    
                    
                #lcd.write_string(u'Do not move\n\rdetecting face')
                
                if (ledCounter > 10):
                    GPIO.output(LEDPin, False)
                    GPIO.output(LEDPinRot, False)
                    
                inputValue = GPIO.input(16)
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
                    confStr = "{0:.2f}".format(conf)
                    
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

                    if conf<55:
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
                        
                        #lcd.write_string(u'Welcome %s!' % (id))
                        #time.sleep(1)
                        #lcd.clear()
                        
                        if(current_milis()- startTimeFaceDetected>5):
                            socketIO.emit('clientPi',"faceDetected")
                            startTimeFaceDetected = current_milis()
                        
                       
                    elif conf>95:
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
                        #lcd.clear()
                        #lcd.write_string(u'Welcome Stranger')
                        #time.sleep(2)
                        #lcd.clear()
                        #lcd.write_string(u'Please push the\n\rbutton')
                        
                        if(not strangerDetected):
                            strangerDetected = True
                    else:
                        cv2.putText(img, str(confStr)+ "%", (x, y + h), font, fontScale, fontColor)
                        #lcd.clear()
                        #lcd.write_string(u'Do not move\n\rdetecting face')
                
                    
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
	#socketIO.wait()
