import numpy as np
from typing import Tuple, Union, List
from math import pi, sqrt
import shapely as sh
from shapely.ops import nearest_points
from shapely import affinity

class Vector:
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
		if isinstance(x,tuple):
			self.x = x[0]
			self.y = x[1]
			self.z = x[2]
		else:
			self.x = float(x)
			self.y = float(y)
			self.z = float(z)
		self.length = np.linalg.norm(self.to_numpy())

	def __sub__(self, other: 'Vector') -> 'Vector':
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
	
	def __add__(self, other: 'Vector') -> 'Vector':
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
	
	def __eq__(self, other):
		"""Overload equality operator to compare points"""
		if not isinstance(other, Vector):
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
		return np.array([self.x, self.y, self.z])  # Return 3D array to match existing code
	
	@staticmethod
	def from_numpy(arr: np.ndarray) -> 'Vector':
		if len(arr) == 3:
			return Vector(arr[0], arr[1],arr[2])
		raise ValueError("Array must have 3 dimensions")
	
	def getAngleWith(self, other_vector: 'Vector') -> float:
		"""Calculate angle between wall and another vector in degrees"""
		dot = self.vector.x * other_vector.x + self.vector.y * other_vector.y + self.vector.z*other_vector.z
		norms = self.length * sqrt(other_vector.x * other_vector.x + other_vector.y * other_vector.y+self.vector.z*other_vector.z)
		cos_angle = dot / norms if norms != 0 else 0
		cos_angle = min(1.0, max(-1.0, cos_angle))  # Handle numerical errors
		angle = np.acos(cos_angle) * 180 / pi
		return angle


class Point(Vector):
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
		if isinstance(x,tuple):
			self.x = x[0]
			self.y = x[1]
			self.z = x[2]
		else:
			self.x = float(x)
			self.y = float(y)
			self.z = float(z)
		if self.x == None or self.y == None or self.z == None:
			raise AttributeError("Invalid point definition")
		self.length = np.linalg.norm(self.to_numpy())
		self._shapelyPoint = sh.Point((self.x,self.y))

class Line:
	def __init__(self, start: Point, end: Point):
		self.start = start
		self.end = end
		self._shapely = sh.LineString([(start.x, start.y), (end.x, end.y)]) # Todo: Implement 3D
		self.length = self._shapely.length
		_direction = end-start
		self._vector = Vector(_direction.x, _direction.y, _direction.z)

	def intersects(self, other: 'Line') -> bool:
		return self._shapely.intersects(other._shapely)

	def distanceTo(self, point: Point) -> float: # Todo: Implement 3D
		return self._shapely.distance(point)