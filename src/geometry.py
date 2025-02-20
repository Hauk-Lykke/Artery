import numpy as np
from typing import Tuple, Union
from math import pi, sqrt, acos
import shapely as sh
import pydantic

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
		self._coords = [self.x, self.y, self.z]

	def toNumpy(self) -> np.ndarray:
		return np.array([self.x, self.y, self.z])  # Return 3D numpy array# Return 3D numpy array
	
	def __repr__(self) -> str:
		output = ("XYZ({},{},{})").format(self.x,self.y,self.z)
		return output
		
	def __iter__(self):
		yield self.x
		yield self.y
		yield self.z

	def __hash__(self):
		"""Overload hash operator to use instances in sets"""
		return hash((self.x, self.y, self.z))
	
	def __getitem__(self, index) -> float:
		'''Overload of index access. Readonly, to set variables, dot notation (point.x) must be used since __setitem__ is not implemented.'''
		return self._coords[index]
	
	@property
	def _shapelyGeometry(self) -> sh.Point:
		return sh.Point(self.toNumpy())

class Vector(XYZ):
	def __init__(self, x: Union[float, Tuple[float, float, float]] = 0, y: float = 0, z: float = 0, _skip_basis: bool = False):
		super().__init__(x,y,z)
		self.length = np.linalg.norm(self.toNumpy())
		if self.x is None or self.y is None or self.z is None:
			raise AttributeError("Invalid Vector definition")
			
		if _skip_basis:
			self.basis = None
		else:
			if self.length < 1e-10:  # Use small epsilon instead of exact zero
				self.basis = Vector(0, 0, 0, _skip_basis=True)
			else:
				x = self.x / self.length if abs(self.x) >= 1e-10 else 0
				y = self.y / self.length if abs(self.y) >= 1e-10 else 0
				z = self.z / self.length if abs(self.z) >= 1e-10 else 0
				self.basis = Vector(x, y, z, _skip_basis=True)
				
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
		if isinstance(geometry, Line) or isinstance(geometry, Point) or isinstance(geometry, Polygon):
			shapelyItem = geometry._shapelyGeometry
		distance = sh.distance(self._shapelyGeometry,shapelyItem)
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
		self._shapelyGeometry = sh.LineString([(start.x, start.y), (end.x, end.y)]) # Todo: Implement 3D
		self.length = self._shapelyGeometry.length
		self.vector = end-start

	def intersects(self, other: 'Line') -> bool:
		return self._shapelyGeometry.intersects(other._shapelyGeometry)

	def distanceTo(self, otherObject: Union[Point, 'Line']) -> float: # Todo: Implement 3D
		if isinstance(otherObject, Line) or isinstance(otherObject,Point):
			return self._shapelyGeometry.distance(otherObject._shapelyGeometry)
		else:
			raise ValueError("Method not overloaded for other classes than Line and Point.")
	
	def __repr__(self) -> str:
		return "Line from {0} to {1}".format(self.start, self.end)
	
	def interpolate(self, point: Point) -> Point:
		# Create Shapely point from input
		shapely_point = sh.Point(point.x, point.y, point.z)
		
		# Get the distance along the line of the nearest point
		distance = self._shapelyGeometry.project(shapely_point)
		
		# Get the actual point coordinates
		interpolated_point = self._shapelyGeometry.interpolate(distance)
		
		# Convert back to our Point class, preserving z-coordinate
		# We linearly interpolate z based on distance along line
		fraction = distance / self.length
		z = self.start.z + fraction * (self.end.z - self.start.z)
		
		return Point(interpolated_point.x, interpolated_point.y, z)
	
	def contains(self, geometry) -> bool:
		'''If the geometry is a point or a line, this method checks if the point or endpoints are on the line segment. '''
		if isinstance(geometry, Point):
			distance = self.distanceTo(geometry)
			return distance == 0
		elif isinstance(geometry, Line):
			distanceToStart = self.distanceTo(geometry.start)
			distanceToEnd = self.distanceTo(geometry.end)
			return (distanceToStart==0 and distanceToEnd==0)
		raise ValueError("Not defined for other types than Line or Point.")

class Polygon:
	points: list[Point]
	_lineSegments: list[Line]
	_shapelyGeometry : sh.Polygon

	def __init__(self, points: list[Point]):
		self.points = list(points)
		self._lineSegments = []
		self._updateShapelyPoly()
		self._updateLineSegments()

	def _updateLineSegments(self):
		if self.points:
			for i, point in enumerate(self.points[1:]):
				self._lineSegments.append(Line(self.points[i-1], point))

	def _updateShapelyPoly(self):
		shapelyPoints = [sh.Point(point.toNumpy()) for point in self.points]
		self._shapelyGeometry = sh.Polygon(shapelyPoints)

	def __getitem__(self,index) -> Point:
		return self.points[index]
	
	def __setitem__(self, index, point):
		self.points[index] = point
		self._updateShapelyPoly()
		self._updateLineSegments(self)

	@staticmethod
	def fromShapelyPolygon(polygon: sh.Polygon) -> 'Polygon':
		newPoints = [Point(shapelyPoint) for shapelyPoint in polygon.exterior.coords]
		newPolygon = Polygon(newPoints)
		return newPolygon
			

	def convexHull(self) -> 'Polygon':
		shapelyConvexHullPolygon = sh.convex_hull(self._shapelyGeometry)
		newPolygon = Polygon.fromShapelyPolygon(shapelyConvexHullPolygon)
		return newPolygon
		
	def contains(self, geometry) -> bool:
		'''If the geometry is a point or a line, this method checks if the point or endpoints are on the polyline defining the polygon. 
		It does NOT check if the geomtry is inside the polygon (like the centroid would be).'''
		if isinstance(geometry, Line) or isinstance(geometry, Point):
			for line in self._lineSegments:
				if line.contains(geometry):
					return True
			return False
		else:
			raise ValueError("Not defined for other geometry than Line or Point yet")
