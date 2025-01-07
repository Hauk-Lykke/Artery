import numpy as np
from typing import Tuple, Union, List

class Point:
    def __init__(self, x: float = 0, y: float = 0, z: float = 0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __eq__(self, other):
        """Overload equality operator to compare points"""
        if not isinstance(other, Point):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z
    
    def __hash__(self):
        """Overload hash operator to use points in sets"""
        return hash((self.x, self.y, self.z))
    
    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z
    
    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])  # Return 2D array to match existing code
    
    @staticmethod
    def from_numpy(arr: np.ndarray) -> 'Point':
        if len(arr) == 3:
            return Point(arr[0], arr[1],arr[2])
        raise ValueError("Array must have 3 dimensions")

def line_intersection(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    """Check if line segments (p1,p2) and (p3,p4) intersect."""
    def ccw(A: Point, B: Point, C: Point) -> bool:
        val = (C.y - A.y) * (B.x - A.x) - (B.y - A.y) * (C.x - A.x)
        if abs(val) < 1e-10:  # Points are collinear
            return False
        return val > 0
    return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))

def point_to_line_distance(point: Point, line_start: Point, line_end: Point) -> float:
    """Calculate the shortest distance from a point to a line segment"""
    p_arr = point.to_numpy()
    start_arr = line_start.to_numpy()
    end_arr = line_end.to_numpy()
    
    line_vec = end_arr - start_arr
    line_len_sq = np.dot(line_vec, line_vec)
    if line_len_sq == 0:
        return np.linalg.norm(p_arr - start_arr)
    
    t = max(0, min(1, np.dot(p_arr - start_arr, line_vec) / line_len_sq))
    projection = start_arr + t * line_vec
    return np.linalg.norm(p_arr - projection)
