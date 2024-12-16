import numpy as np
from typing import List,Tuple

class Room:
    def __init__(self, corners: List[Tuple[float, float]]):
        self.corners = np.array(corners)
        self.center = np.mean(corners, axis=0)

class AHU:
    def __init__(self, position: Tuple[float, float]):
        self.position = np.array(position)
