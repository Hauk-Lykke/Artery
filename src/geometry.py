import numpy as np
from typing import Tuple, Union, List
from math import pi, sqrt, acos
import shapely as sh
from shapely.ops import nearest_points
from shapely import affinity
from shapely.geometry import Point as ShapelyPoint
import string

class XYZ:
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
		if isinstance(x, Point):
			point = x
			self.x = point.x
			self.y = point.y
			self.z = point.z
		if isinstance(x, Vector):
			vector = x
			self.x = vector.x
			self.y = vector.y
			self.z = vector.z
		
		if isinstance(x,tuple):
			if len(x) == 3:
				self.x = float(x[0])
				self.y = float(x[1])
				self.z = float(x[2])
			elif len(x) == 2:
				self.x = float(x[0])
				self.y = float(x[1])
				self.z = float(0)
			else:
				raise ValueError("XYZ must have 2 coordinates, at least x and y coordinates.")
		
		else:
			if None in (x, y):
				raise ValueError("XYZ must have 2 coordinates, at least x and y coordinates.")
			if z is None:
				z = 0
			self.x = float(x)
			self.y = float(y)
			self.z = float(z)

	def to_numpy(self) -> np.ndarray:
		return np.array([self.x, self.y, self.z])  # Return 3D numpy array# Return 3D numpy array
	
	def __repr__(self) -> str:
		output = ("XYZ({},{},{})").format(self.x,self.y,self.z)
		return output
		
	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z

	@staticmethod
	def from_numpy(arr: np.ndarray) -> 'Vector':
		if len(arr) == 3:
			return Vector(arr[0], arr[1],arr[2])
		raise ValueError("Array must have 3 dimensions")
		
	def __hash__(self):
		"""Overload hash operator to use instances in sets"""
		return hash((self.x, self.y, self.z))

class Vector(XYZ):
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
		super().__init__(x,y,z)
		self.length = np.linalg.norm(self.to_numpy())
		if self.x is None or self.y is None or self.z is None:
			raise AttributeError("Invalid Vector definition")

	def __sub__(self, other: 'Vector') -> 'Vector':
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
	
	def __add__(self, other: 'Vector') -> 'Vector':
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
	
	def __eq__(self, other: 'Vector') -> bool:
		if isinstance(other, Vector):
			return self.x == other.x and self.y == other.y and self.z == other.z
		return False

	def __hash__(self) -> int:
		return hash((self.x, self.y, self.z))
	
	def getAngleWith(self, other_vector: 'Vector') -> float:
		"""Calculate the angle between this vector and another vector in degrees"""
		dot = self.x * other_vector.x + self.y * other_vector.y + self.z * other_vector.z
		norms = self.length * sqrt(other_vector.x * other_vector.x + other_vector.y * other_vector.y + other_vector.z * other_vector.z)
		cos_angle = dot / norms if norms != 0 else 0
		cos_angle = min(1.0, max(-1.0, cos_angle))  # Handle numerical errors
		angle = acos(cos_angle) * 180 / pi
		return angle
	
	def __repr__(self) -> str:
		output = ("Vector({},{},{})").format(self.x,self.y,self.z)
		return output

class Point(XYZ):
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
		XYZ.__init__(self, x, y, z)
		self.vector = Vector(self.x, self.y, self.z)
		if self.x is None or self.y is None or self.z is None:
			raise AttributeError("Invalid Point definition")

	def __sub__(self, other: 'Point') -> Vector:
		return Vector(
			self.x - other.x,
			self.y - other.y,
			self.z - other.z
		)

	def __repr__(self) -> str:
		output = ("Point({},{},{})").format(self.x,self.y,self.z)
		return output
	
	def distanceTo(self,geometry) -> float:
		if isinstance(geometry, Line):
			shapelyItem = geometry._shapely
		if isinstance(geometry, Point):
			shapelyItem = sh.Point(geometry.to_numpy())
		shapelyPoint = sh.Point(self.to_numpy())
		distance = sh.distance(shapelyPoint,shapelyItem)
		return distance
	
	def __add__(self, vector: Vector) -> 'Point':
		if isinstance(vector,Vector):
			return Point(self.x+vector.x, self.y+vector.y, self.z+vector.z)
		else:
			return super.__add__(vector)

	def __eq__(self, other: 'Point') -> bool:
		if isinstance(other, Point):
			return self.x == other.x and self.y == other.y and self.z == other.z
		return False

	def __hash__(self) -> int:
		return hash((self.x, self.y, self.z))

class Line:
	def __init__(self, start: Point, end: Point):
		if start == end:
			raise ValueError("Start and end points cannot be the same.")
		self.start = start
		self.end = end
		self._shapely = sh.LineString([(start.x, start.y), (end.x, end.y)]) # Todo: Implement 3D
		self.length = self._shapely.length
		self.vector = end-start

	def intersects(self, other: 'Line') -> bool:
		return self._shapely.intersects(other._shapely)

	def distanceTo(self, point: Point) -> float: # Todo: Implement 3D
		shapelyPoint = sh.Point(point.x,point.y)
		return self._shapely.distance(shapelyPoint)
	
	def __repr__(self) -> str:
		return "Line from {0} to {1}".format(self.start, self.end)