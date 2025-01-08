import numpy as np
from typing import Tuple, Union, List

class Vector:
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0):
		if isinstance(x, tuple):
			self.x = float(x[0])
			self.y = float(x[1])
			self.z = float(x[2])
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
		"""Overload equality operator to compare Vectors"""
		if not isinstance(other, Vector):
			return False
		return self.x == other.x and self.y == other.y and self.z == other.z
	
	def __hash__(self):
		"""Overload hash operator to use Vectors in sets"""
		return hash((self.x, self.y, self.z))
	
	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z
	
	def to_numpy(self) -> np.ndarray:
		return np.array([self.x, self.y, self.z])  # Return 2D array to match existing code
	
	@staticmethod
	def from_numpy(arr: np.ndarray) -> 'Vector':
		if len(arr) == 3:
			return Vector(arr[0], arr[1],arr[2])
		raise ValueError("Array must have 3 dimensions")
	
	def __abs__(self):
		"""
		Returns the magnitude (Euclidean norm) of the vector.

		Returns:
			float: The length (magnitude) of the vector calculated using the Euclidean norm.
		This is the same as the __len__ method.
		"""
		return self.length
	


class Line:
	def __init__(self,start: 'Point', end: 'Point'):
		self.start = start
		self.end = end
		self.length = len(self)
	
	def __len__(self)-> float:
		return np.linalg.norm(self.end.to_numpy() - self.start.to_numpy())

class Point(Vector):
	def __init__(self, x: float = 0, y: float = 0, z: float = 0):
		super().__init__(x,y,z)

	def distanceToLine(self, line: Line) -> float:
		"""Calculate the shortest distance from a Vector to a line segment"""
		p_arr = self.to_numpy()
		start_arr = line.start.to_numpy()
		end_arr = line.end.to_numpy()
		
		line_vec = end_arr - start_arr
		line_len_sq = np.dot(line_vec, line_vec)
		if line_len_sq == 0:
			return np.linalg.norm(p_arr - start_arr)
		
		t = max(0, min(1, np.dot(p_arr - start_arr, line_vec) / line_len_sq))
		projection = start_arr + t * line_vec
		return np.linalg.norm(p_arr - projection)
	
	
def ccw(A: Point, B: Point, C: Point) -> bool:
	if A.z or B.z or C.z:
		raise AttributeError("Z-coord not implemented yet")
	val = (C.y - A.y) * (B.x - A.x) - (B.y - A.y) * (C.x - A.x)
	if abs(val) < 1e-10:  # Points are collinear
		return False
	return val > 0

def line_intersection(p0: 'Point', p1: 'Point', p3: 'Point', p4: 'Point') -> bool:
	"""Check if line segments (p0,p1) and (p3,p4) intersect."""
	if isinstance(p0, Point):
		pass
	elif isinstance(p0, Line) and isinstance(p1, Line):
		line0=p0
		line1=p1
		p0 = line0.start
		p1 = line0.end
		p3 = line1.start
		p4 = line1.end	
	return (ccw(p0, p3, p4) != ccw(p1, p3, p4)) and (ccw(p0, p1, p3) != ccw(p0, p1, p4))	
