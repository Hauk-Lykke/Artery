import numpy as np
from typing import Tuple, Union, List
from math import pi, sqrt
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
	
	def __add__(self, vector):
		self.x = 

class Line:
	def __init__(self, start: Point, end: Point):
		self.start = start
		self.end = end
		self._shapely = LineString([(start.x, start.y), (end.x, end.y)]) # Todo: Implement 3D
		self.length = self._shapely.length
		self._vector = Vector(end-start)

	def intersects(self, other: 'Line') -> bool:
		return self._shapely.intersects(other._shapely)

	def distanceTo(self, point: Union[Point, Vector]) -> float:
		if isinstance(point, Vector):
			point = Point(point.x, point.y)
		return self._shapely.distance(point)
	
	def getAngleWith(self, other_vector: Vector) -> float:
		"""Calculate angle between wall and another vector in degrees"""
		dot = self.vector.x * other_vector.x + self.vector.y * other_vector.y + self.vector.z*other_vector.z
		norms = self.length * sqrt(other_vector.x * other_vector.x + other_vector.y * other_vector.y+self.vector.z*other_vector.z)
		cos_angle = dot / norms if norms != 0 else 0
		cos_angle = min(1.0, max(-1.0, cos_angle))  # Handle numerical errors
		angle = np.acos(cos_angle) * 180 / pi
		return angle
