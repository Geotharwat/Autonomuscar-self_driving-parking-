import time
import threading
from navigation.positioning import estimate as estimatePosition

EPSILON = 3.5
MEASURE_INTERVAL = 0.1
NAVIGATION_THREAD = None
NAVIGATION_THREAD_LOCK = threading.Lock()

lastMeasureTime = time.time()

__desired_speed = 10
__motor_power = 0

__lastPosition = [0, 0]


def setDesiredSpeed(speed):
    with NAVIGATION_THREAD_LOCK:
        __desired_speed = speed;
def getMotorPower(speed):
    with NAVIGATION_THREAD_LOCK:
       return __motor_power
# class Owl:
#     def __init__():
#         self.trigger = trigger
#         self.echo = echo
#         self.last_m_time = 0;
#         self.last_m = 0;
#         #set GPIO direction (IN / OUT)
#         GPIO.setup(trigger, GPIO.OUT)
#         GPIO.setup(echo, GPIO.IN)
 
#     def distance(self):
#         # set Trigger to HIGH
#         if time.time() - self.last_m_time < 0.05:
#             return self.last_m
#         self.last_m_time = time.time();
#         GPIO.output(self.trigger, True)
    
#         # set Trigger after 0.01ms to LOW
#         time.sleep(0.00001)
#         GPIO.output(self.trigger, False)
    
#         StartTime = time.time_ns()
#         StopTime = time.time_ns()
#         s = time.time()

#         # save StartTime
#         while GPIO.input(self.echo) == 0 and time.time() - s < 0.1:
#             StartTime = time.time_ns()

#         # save time of arrival
#         while GPIO.input(self.echo) == 1 and time.time() - s < 0.1:
#             StopTime = time.time_ns()

#         if  time.time() - s >= 0.3:
#             return 0
#         # time difference between start and arrival
#         TimeElapsed = StopTime - StartTime
#         # multiply with the sonic speed (3.43e-5 cm/s)
#         # and divide by 2, because there and back
#         self.last_m = (TimeElapsed * 3.43e-5) / 2
#         return  self.last_m 



# def adjustMotorPower():
#     global __motor_power
#     with NAVIGATION_THREAD_LOCK:
#         desiredSpeed = __desired_speed
#     delta = desiredSpeed - abs(getSpeed())
#     # print(f"speed={speed} motor_power={motor_power} dis={position[1]}", end="\r")
#     if abs(delta) > 0.1 * desiredSpeed:
#         with NAVIGATION_THREAD_LOCK:
#             __motor_power += delta / (desiredSpeed * 2) * EPSILON 
#             __motor_power = (
#                 100 if __motor_power > 100 else 0 if __motor_power < 0 else __motor_power
            # )

def process():
    while True:
        estimatePosition();
        # adjustMotorPower(desiredSpeed=10)
def start():
    global NAVIGATION_THREAD
    if NAVIGATION_THREAD is not None: return
    NAVIGATION_THREAD = threading.Thread(target=process)
    NAVIGATION_THREAD.daemon = True
    NAVIGATION_THREAD.start()