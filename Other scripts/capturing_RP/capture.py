from time import sleep
from picamera import PiCamera

camera = PiCamera()
camera.resolution = (1280, 720)
camera.start_preview()
# Camera warm-up time
sleep(2)
camera.capture('capture.jpg')