import os, time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(40, GPIO.OUT)

GPIO.output(40, GPIO.LOW)
time.sleep(0.1)
os.system("mplayer harmonogram45.mp3")
time.sleep(0.5)
GPIO.output(40, GPIO.LOW)
GPIO.cleanup()
