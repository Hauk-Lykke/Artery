import numpy as np
from typing import List, Tuple

class Room:
    def __init__(self, corners: List[Tuple[float, float]]):
        self.corners = np.array(corners)
        self.center = np.mean(corners, axis=0)

class AHU:
    def __init__(self, position: Tuple[float, float]):
        self.position = np.array(position)

class Node:
    def __init__(self, position: np.ndarray, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f
    
class Wall:
    def __init__(self,startpoint,endpoint):
        self.start = startpoint
        self.end = endpoint
        

