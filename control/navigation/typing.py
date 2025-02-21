from abc import ABC, abstractmethod
from typing import List, Optional


class IProximity(ABC):
    @abstractmethod
    def distance(self) -> Optional[float]:
        pass


class Smoother:
    def __init__(self, n: int):
        self.n = n
        self.values: List[float] = []
        self._rem = None

    def add(self, v: float):
        self.values.append(v)

    def smooth(self, v: float) -> float:
        self.values.append(v)
        if len(self.values) > self.n:
            self._rem = self.values.pop(0)
        return sum(self.values) / len(self.values)

    def unshift(self):
        if self._rem is not None:
            self.values.pop()
            self.values.insert(0, self._rem)

    def clear(self):
        self._rem = None
        self.values = []


class AxisSpeedEstimator:
    def __init__(
        self,
        proximity: IProximity,
        weight: float = 1,
        n: int = 3,
        maxDeltaSpeed: float = 20,
        maxSpeed: float = 40,
    ):
        self.proximity = proximity
        self.weight = weight
        self.n = n
        self.maxDeltaSpeed = maxDeltaSpeed
        self.maxSpeed = maxSpeed
        self.previous = Smoother(5)
        self.speed: Optional[float] = 0
        self.measure: Optional[float] = None

    def estimate(self, deltaTime: float) -> Optional[float]:
        m = self.proximity.distance()
        if m is not None:
            measure = self.previous.smooth(m)
            pm = self.measure if self.measure is not None else measure
            ps = self.speed
            displacement = pm - measure
            speed = displacement / deltaTime
            a = speed - ps;
      
            if abs(a) > 5:
                print(a)
                self.speed = speed
                # self.measure = measure
                # self.previous.clear()
                # self.previous.add(m)
                return None
            self.measure = measure
            self.speed = speed
            return speed
        else:
            self.speed: Optional[float] = 0
            self.measure: Optional[float] = 0
            return None
