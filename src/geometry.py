import numpy as np
from typing import Tuple, Union, List
from shapely.geometry import Point, LineString
from shapely.ops import nearest_points
from shapely import affinity

class Vector:
    def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
        self.x = float(x) if not isinstance(x, tuple) else float(x[0])
        self.y = float(y) if not isinstance(x, tuple) else float(x[1])
        self.z = float(z) if not isinstance(x, tuple) else float(x[2])
        self.length = np.linalg.norm(self.to_numpy())
    
    def to_point(self) -> Point:
        return Point(self.x, self.y)

class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end
        self._shapely = LineString([(start.x, start.y), (end.x, end.y)])
        self.length = self._shapely.length

    def intersects(self, other: 'Line') -> bool:
        return self._shapely.intersects(other._shapely)

    def distance_to(self, point: Union[Point, Vector]) -> float:
        if isinstance(point, Vector):
            point = Point(point.x, point.y)
        return self._shapely.distance(point)

def line_intersection(p0: Vector, p1: Vector, p3: Vector, p4: Vector) -> bool:
    """Check if line segments intersect using shapely"""
    line1 = LineString([(p0.x, p0.y), (p1.x, p1.y)])
    line2 = LineString([(p3.x, p3.y), (p4.x, p4.y)])
    return line1.intersects(line2)