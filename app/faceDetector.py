from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as GPIO
from time import sleep
import time
import cv2
import numpy as np

GPIO.setmode(GPIO.BCM)
LEDPin = 22
GPIO.setup(LEDPin, GPIO.OUT)

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

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    img = frame.array
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    
    if (ledCounter > 10):
        GPIO.output(LEDPin, False)
    
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        id, conf = rec.predict(gray[y:y+h, x:x+w])
        confStr = "{0:.2f}".format(conf)

        if(id==1):
            id = "Syarif"
            GPIO.output(LEDPin, True)
            ledCounter = 0
        elif(id==2):
            id = "Alice"
        elif(id==3):
            id="Simon"   

        if conf<70:
            cv2.putText(img, str(id), (x, y + h), font, fontScale, fontColor)
        elif conf>95:
            cv2.putText(img, "Warning, Stranger!", (x, y + h), font, fontScale, (0, 0, 255))
        else:
            cv2.putText(img, str(confStr)+ "%", (x, y + h), font, fontScale, fontColor)
        
    ledCounter += 1
    cv2.imshow('name',img)
    rawCapture.truncate(0)
    #exit if you press q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

GPIO.cleanup()
cv2.destroyAllWindows()
