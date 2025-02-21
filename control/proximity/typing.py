from abc import ABC, abstractmethod
from typing import List, Optional

class IProximity(ABC):
    @abstractmethod
    def distance(self) -> Optional[float]:
        pass


class MeanApproximator():

    def __init__(self, prox: IProximity, n = 3):
        self.__prox = prox
        self.__values = []
        self.__n = n
    
    def measure(self) -> Optional[float]: 
        values = []
        for i in range(self.__n):
            d = self.__prox.distance()
            if d is not None:
                values.append(d)
        if len(values) == 0:
            return -1
        mean = sum(values) / len(values)
        return mean
