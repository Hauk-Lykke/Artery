from geometry import Point, Line
import math
import random
import shapely as sh


class WallType:
	'''Enum class for wall types'''
	DRYWALL = 1
	CONCRETE = 2
	OUTER_WALL = 3

class Wall2D(Line):
	def __init__(self, start: Point, end: Point, wallType: WallType = WallType.DRYWALL):
		super().__init__(start,end)
		self.wallType = wallType
		self.line = Line(start,end)

	def reverse(self) -> 'Wall2D':
		"""Switch places of start and end points"""
		return Wall2D(self.end, self.start)
	
	def __eq__(self, other):
		"""Overload equality operator to compare walls"""
		if not isinstance(other, Wall2D):
			return False
		return self.start == other.start and self.end == other.end and self.wallType == other.wallType
	
	def __hash__(self):
		"""Overload hash operator to use walls in sets"""
		return hash((self.start, self.end, self.wallType))
	
	def __repr__(self) -> str:
		return "Wall from {0} to {1} of type {2}".format(self.start, self.end, self.wallType)

class Room:
	def __init__(self, corners: list[Point]):
		self.corners = corners
		# Calculate center as average of x and y coordinates
		center_x = sum(corner.x for corner in corners) / len(corners)
		center_y = sum(corner.y for corner in corners) / len(corners)
		self.center = Point(center_x, center_y)
		self._create_walls()
		self.soundRating = 37 # Default sound rating in decibel
		self.supplyAirDemand = 0
		self._shapelyPoly = sh.geometry.Polygon([[p.x, p.y, p.z] for p in self.corners])
		self.checkRectangular()
		self._area = self._shapelyPoly.area
	
	def _create_walls(self):
		self.walls = []
		for i, corner in enumerate(self.corners):
			start = corner
			end = self.corners[(i + 1) % len(self.corners)]
			self.walls.append(Wall2D(start, end))
		return

	def isInsideRoom(self,point: Point) ->bool:
		# Ray casting algorithm to determine if point is inside polygon
		n = len(self.corners)
		inside = False
		j = n - 1
		for i in range(n):
			if ((self.corners[i].y > point.y) != (self.corners[j].y > point.y) and
				point.x < (self.corners[j].x - self.corners[i].x) * 
				(point.y - self.corners[i].y) / (self.corners[j].y - self.corners[i].y) 
				+ self.corners[i].x):
				inside = not inside
			j = i
		return inside
	
	def checkRectangular(self):
		poly = self._shapelyPoly
		if math.isclose(poly.minimum_rotated_rectangle.area, poly.area):
			self.isRectangular = True
		else:
			self.isRectangular = False

	@property
	def area(self) -> float:
		self._area = self._shapelyPoly.area
		return self._area

	def aspectRatioOk(self, max_ratio) -> bool:
		# self._shapelyPoly.
		"""Checks if room's bounding box meets max aspect ratio."""
		if not self.isRectangular:
			raise ValueError("Room is not rectangular, aspect ratio check of non-rectangular rooms not implemented")
		# (x1, y1, x2, y2) = room
		width = abs(self.corners[2].x-self.corners[0].x)
		# w = abs(x2 - x1)
		length = abs(self.corners[2].y-self.corners[0].y)
		# h = abs(y2 - y1)
		if min(width, length) == 0:
			return False
		return (max(width, length) / min(width, length)) <= max_ratio
	
	
	def conformsToAspectRatio(self, min_aspect_ratio, max_aspect_ratio) -> bool:
		"""Checks if room area and aspect ratio are within limits."""
		return (min_aspect_ratio <= self.area) and self.aspectRatioOk(max_aspect_ratio)
	
	
	def subdivide(self, direction) -> tuple['Room']:
		"""
		Splits room randomly in 'vertical' or 'horizontal' direction.
		Returns two new rooms if the split is valid, else None.
		"""
		if not self.isRectangular:
			raise ValueError("Method not defined for non-rectangular rooms.")
		
		x0 = self.corners[0].x
		y0 = self.corners[0].y
		x1 = self.corners[2].x
		y1 = self.corners[2].y
		width = abs(x1 - x0)
		length = abs(y1 - y0)

		# If too small, skip
		if width < 3 or length < 3:
			return None

		if direction == 'vertical':
			# Split x between x1+1 and x2-1
			# split_x = random.randint(x0 + 1, x1 - 1)
			split_x = x0+1 + random.random()*(width-1)
			# room0 = (x0, y0, split_x, y1)
			room0 = Room([Point(x0, y0),Point(split_x,y0),Point(split_x,y1),Point(x0,y1)])
			# room1 = (split_x, y0, x1, y1)
			room1 = Room([Point(split_x, y0),Point(x1,y0),Point(x1,y1),Point(split_x,y1)])
			return (room0, room1)
		else:
			# Split y between y1+1 and y2-1
			# split_y = random.randint(y0 + 1, y1 - 1)
			split_y = y0+1 + random.random()*(length-1)
			room0 = Room([Point(x0, y0),Point(x1,y0),Point(x1,split_y),Point(x0,split_y)])
			room1 = Room([Point(x0, split_y),Point(x1,split_y),Point(x1,y1),Point(x0,y1)])
			return (room0, room1)


