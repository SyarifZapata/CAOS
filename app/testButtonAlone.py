import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)



GPIO.setup(16, GPIO.IN, pull_up_down = GPIO.PUD_UP)

try:
    while (True):
        inputValue = GPIO.input(16)
        if(inputValue == False):
            print("Button Pressed")
        sleep(0.3)
finally:
	GPIO.cleanup()
