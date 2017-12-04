from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
from time import sleep
import time
import cv2
import numpy as np
#import pyfirmata

GPIO.setmode(GPIO.BCM)
LEDPin = 22
LEDPinRot = 17
motionDetector = 21
GPIO.setup(LEDPin, GPIO.OUT)
GPIO.setup(LEDPinRot, GPIO.OUT)
GPIO.setup(motionDetector, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

#board = pyfirmata.Arduino('/dev/ttyACM0')
#pin6 = board.get_pin('d:6:o')
#pinGSM = board.get_pin('d:4:o')

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

try:
    while True:
        if(GPIO.input(motionDetector)):
            for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                img = frame.array
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceDetect.detectMultiScale(gray, 1.3, 5)
                
                if (ledCounter > 10):
                    GPIO.output(LEDPin, False)
                    GPIO.output(LEDPinRot, False)
                    #pin6.write(0)
                
                for (x,y,w,h) in faces:
                    cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
                    id, conf = rec.predict(gray[y:y+h, x:x+w])
                    confStr = "{0:.2f}".format(conf)

                    if(id==1):
                        id = "Syarif"
                        ledCounter = 0
                    elif(id==2):
                        id = "Alice"
                    elif(id==3):
                        id="Simon"   

                    if conf<70:
                        cv2.putText(img, str(id), (x, y + h), font, fontScale, fontColor)
                        GPIO.output(LEDPin, True)
                        #pin6.write(1)
                        #pinGSM.write(1)
                        GPIO.output(LEDPinRot, False)
                        #pinGSM.write(0)
                    elif conf>95:
                        cv2.putText(img, "Warning, Stranger!", (x, y + h), font, fontScale, (0, 0, 255))
                        GPIO.output(LEDPinRot, True)
                        GPIO.output(LEDPin, False)
                    else:
                        cv2.putText(img, str(confStr)+ "%", (x, y + h), font, fontScale, fontColor)
                        
                    
                ledCounter += 1
                cv2.imshow('name',img)
                rawCapture.truncate(0)
                #exit if you press q
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cv2.destroyAllWindows()
            
except KeyboardInterrupt:  
    # here you put any code you want to run before the program   
    # exits when you press CTRL+C  
    print("exit by user") # print value of counter 
            
finally:
	GPIO.cleanup()
