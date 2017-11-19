import cv2
import numpy as np

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
cam = cv2.VideoCapture(0)
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("recognizer/trainingData.yml")
id = 0
font = cv2.FONT_HERSHEY_SIMPLEX
fontScale = 1
fontColor = (255, 255, 255)

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceDetect.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,255,0), 2)
        id, conf = rec.predict(gray[y:y+h, x:x+w])
        confStr = "{0:.2f}".format(conf)

        if(id==1):
            id = "Syarif"
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
    cv2.imshow('name',img)

    #exit if you press q
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.release()
cv2.destroyAllWindows()