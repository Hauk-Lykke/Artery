import numpy as np
from typing import List, Tuple

class Wall:
    def __init__(self, startpoint: Tuple[float, float], endpoint: Tuple[float, float]):
        self.start = np.array(startpoint)
        self.end = np.array(endpoint)
        self._vector = self.end - self.start
        
    @property
    def vector(self) -> np.ndarray:
        """Get wall direction vector"""
        return self._vector
    
    @property
    def length(self) -> float:
        """Get wall length"""
        return np.linalg.norm(self.vector)
    
    def get_angle_with(self, other_vector: np.ndarray) -> float:
        """Calculate angle between wall and another vector in degrees"""
        dot = np.dot(self.vector, other_vector)
        norms = np.linalg.norm(self.vector) * np.linalg.norm(other_vector)
        cos_angle = dot / norms if norms != 0 else 0
        cos_angle = min(1.0, max(-1.0, cos_angle))  # Handle numerical errors
        angle = np.arccos(cos_angle) * 180 / np.pi
        return angle

class Room:
    def __init__(self, corners: List[Tuple[float, float]]):
        self.corners = np.array(corners)
        self.center = np.mean(corners, axis=0)
        self.walls = self._create_walls()
    
    def _create_walls(self) -> List[Wall]:
        walls = []
        for i in range(len(self.corners)):
            start = self.corners[i]
            end = self.corners[(i + 1) % len(self.corners)]
            walls.append(Wall(start, end))
        return walls

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
