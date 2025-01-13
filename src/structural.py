from typing import List
from core import Cost
from geometry import Point, Line, Vector
from MEP import AirHandlingUnit


class WallType:
	'''Enum class for wall types'''
	DRYWALL = 1
	CONCRETE = 2
	OUTER_WALL = 3

class Wall(Line):
	def __init__(self, start: Point, end: Point, wall_type: WallType = WallType.DRYWALL):
		super().__init__(start,end)
		self.wall_type = wall_type
		self.line = Line(start,end)

	def reverse(self) -> 'Wall':
		"""Switch places of start and end points"""
		return Wall(self.end, self.start)
	
	def __eq__(self, other):
		"""Overload equality operator to compare walls"""
		if not isinstance(other, Wall):
			return False
		return self.start == other.start and self.end == other.end and self.wall_type == other.wall_type
	
	def __hash__(self):
		"""Overload hash operator to use walls in sets"""
		return hash((self.start, self.end, self.wall_type))
	
	def __repr__(self) -> str:
		return "Wall from {0} to {1} of type {2}".format(self.start, self.end, self.wall_type)

class Room:
	def __init__(self, corners: list[Point]):
		self.corners = corners
		# Calculate center as average of x and y coordinates
		center_x = sum(corner.x for corner in corners) / len(corners)
		center_y = sum(corner.y for corner in corners) / len(corners)
		self.center = Point(center_x, center_y)
		self._create_walls()
	
	def _create_walls(self):
		self.walls = []
		for i, corner in enumerate(self.corners):
			start = corner
			end = self.corners[(i + 1) % len(self.corners)]
			self.walls.append(Wall(start, end))
		return

	def is_inside_room(self,point: Point) ->bool:
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

class FloorPlan:
	def __init__(self, rooms: list[Room] = None, ahu: AirHandlingUnit = None):
		self.walls = set()
		self.ahu = None  # Initialize as None by default
		self.rooms = []
		if rooms is not None:
			self.addRooms(rooms)
		if ahu is not None:
			self.ahu = ahu

	def addRoom(self, room):
		self.rooms.append(room)
		self.updateWalls()

	def updateWalls(self):
		# uniqueWalls = set()
		for room in self.rooms:
			for wall in room.walls:
				reverse_wall = wall.reverse()
				if wall not in self.walls and reverse_wall not in self.walls:
					self.walls.add(wall)
		# self.walls = list(self.walls) # Would be nice if walls were somehow ordered, but that's for later

	def addRooms(self, rooms):
		for room in rooms:
			self.addRoom(room)



class Building:
		def __init__(self, floorPlans: list = [FloorPlan]):
			self.floor_plans = floorPlans



class WallCrossingCost(Cost):
	"""Base class for wall crossing costs"""
	def __init__(self, wall: Wall):
		self.wall = wall

class WallCosts:
	"""Central definition of wall-related costs"""
	PROXIMITY_THRESHOLD = 0.5  # Distance at which wall proximity starts affecting cost
	ANGLE_MULTIPLIER = 2.0  # Multiplier for angled crossings
	
	@staticmethod
	def get_base_cost(wall_type: WallType) -> float:
		"""Get the base perpendicular crossing cost for a wall type"""
		if wall_type == WallType.DRYWALL:
			return 1.0
		elif wall_type == WallType.CONCRETE:
			return 5.0
		else:  # OUTER_WALL
			return 20.0
	
	@staticmethod
	def get_angled_cost(wall_type: WallType) -> float:
		"""Get the angled crossing cost for a wall type"""
		return WallCosts.get_base_cost(wall_type) * WallCosts.ANGLE_MULTIPLIER

class StandardWallCost(WallCrossingCost):
	"""Standard implementation of wall crossing costs"""
	
	def __init__(self, wall: Wall):
		super().__init__(wall)
		self.perpendicular_cost = WallCosts.get_base_cost(wall.wall_type)
		self.angled_cost = WallCosts.get_angled_cost(wall.wall_type)
	
	def calculate(self, current: Point, next: Point) -> float:
		otherLine = Line(current, next)
		# Check if path crosses wall
		if self.wall.intersects(otherLine):
			path_vector = next-current
			angle = self.wall.vector.getAngleWith(path_vector)
			angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
			return self.perpendicular_cost if abs(90 - angle) <= 3 else self.angled_cost
		
		# If not crossing, check proximity
		current_dist = current.distanceTo(self.wall)
		next_dist = next.distanceTo(self.wall)
		
		min_dist = min(current_dist, next_dist)
		if min_dist >= WallCosts.PROXIMITY_THRESHOLD:
			return 0.0
		
		# Linear interpolation between 0 and perpendicular_cost based on distance
		return self.perpendicular_cost * (1 - min_dist / WallCosts.PROXIMITY_THRESHOLD)
