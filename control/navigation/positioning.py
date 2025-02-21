import threading
import time
from typing import List, Optional, Tuple
from navigation.typing import IProximity, AxisSpeedEstimator
from navigation.proximity import front

lock = threading.Lock()

MAX_SPEED_DELTA = 5
MAX_SPEED = 40
N_SMOOTHING = 3

__position: Tuple[float, float] = (0, 0)
__speed: Tuple[float, float] = (0, 0)
__last_estimate_time = time.time()

yAxisEstimators: List[AxisSpeedEstimator] = [AxisSpeedEstimator(front, 1, N_SMOOTHING, MAX_SPEED_DELTA, MAX_SPEED)]


def getPosition() -> Tuple[float, float]:
    with lock:
        return [__position[0], __position[1]]


def getSpeed() -> float:
    with lock:
        return __speed


def estimate():
    global __last_estimate_time, __speed, __position
    deltaTime = time.time() - __last_estimate_time
    if deltaTime < 0.1:
        return
    __last_estimate_time = time.time()

    yWeightSum = 0
    ySpeedSum = 0
    for est in yAxisEstimators:
        speed = est.estimate(deltaTime)
        if speed is not None:
            print(
                f"est= m={est.measure} deltaTime={deltaTime} speed={speed} \t\t\t"
            )

        else:
             print(f"failed est= m={est.measure} deltaTime={deltaTime} speed={speed} \t\t\t")

        if (
            speed is not None
        ):
            ySpeedSum += speed * est.weight
            yWeightSum += est.weight
    with lock:
        __speed = (
            __speed[0],
            ySpeedSum / yWeightSum if yWeightSum != 0 else __speed[1],
        )
        __position = (__position[0], __position[1] + __speed[1] * deltaTime)
    print(f"position={__position} speed={__speed}")
