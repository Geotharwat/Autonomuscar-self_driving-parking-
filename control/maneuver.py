from constants import STEERING_RADIUS
import math


def distance(p0, p1):
    return math.sqrt((p0[0] - p1[0]) ** 2 + (p0[1] - p1[1]) ** 2)


def curve(chord):
    return 2 * STEERING_RADIUS * math.asin(chord / (2 * STEERING_RADIUS))


PARK_SPEED = 4  # 2 cm/s


class Movement:
    def __init__(self, steering, speed, displacement, point):
        self.steering = steering
        self.speed = speed
        self.displacement = displacement
        self.point = point


def calculateManuever(s):
    # refer https://www.desmos.com/calculator/wkrv7gv37c
    R = STEERING_RADIUS
    z = R - math.sqrt(3 * R**2 - s**2 - 2 * s * R)
    p0 = (0, 0)  # circle A center
    pt = (s, z)  # touch point between bottom circle and line
    pi = ((s + R) / 2, (R + z) / 2)  # intersection between two circles
    L0 = abs(z) -14 # 14 is some weird value i put here 
    L1 = curve(distance(pt, pi))
    L2 = curve(distance(pt, pi))
    return [
        Movement(0, -1, L0, (s - 10, z)),  # go backward
        Movement(
            1, 1, L1, (pt[0] - 10, pt[1])
        ),  # go forward right
        Movement(
            -1, -1, L2, (pi[0] - 10, pi[1])
        ),  # go backward left
        Movement(0, -1, 20, (-10 - 10, 0)),  # go backward
    ]
