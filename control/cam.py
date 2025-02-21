from picamera import PiCamera
from time import sleep

camera = PiCamera()
sleep(5)
camera.start_preview()
camera.capture('./cm-tst.jpg')
camera.stop_preview()