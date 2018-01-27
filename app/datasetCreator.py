from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np

camera = PiCamera()
camera.resolution = (640,480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640,480))

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
id = input('enter user id')
sampleNum = 0

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    
    for (x,y,w,h) in faces:
        sampleNum = sampleNum+1
        cv2.imwrite("dataSet/User." + str(id) + "."+str(sampleNum)+".jpg", gray[y:y+h, x:x+w]) #only save the image in rectangle
        cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2)
        cv2.waitKey(100)
    cv2.imshow('Frame',image)
    key = cv2.waitKey(1) & 0xFF
    rawCapture.truncate(0)
    
    if(sampleNum>40):
        break

cv2.destroyAllWindows()