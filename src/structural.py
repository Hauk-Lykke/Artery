from abc import ABC, abstractmethod
from typing import List
from core import Cost
from geometry import line_intersection, point_to_line_distance, Point
from MEPcomponents import AirHandlingUnit
from math import sqrt


class WallType:
	'''Enum class for wall types'''
	DRYWALL = 1
	CONCRETE = 2
	OUTER_WALL = 3

class Wall:
	def __init__(self, startpoint: Point, endpoint: Point, wall_type: WallType = WallType.DRYWALL):
		self.start = startpoint
		self.end = endpoint
		self._vector = Point(endpoint.x - startpoint.x, endpoint.y - startpoint.y)
		self.wall_type = wall_type
	
	@property
	def vector(self) -> Point:
		"""Get wall direction vector"""
		return self._vector
	
	@property
	def length(self) -> float:
		"""Get wall length"""
		return sqrt(self._vector.x * self._vector.x + self._vector.y * self._vector.y)
	
	def get_angle_with(self, other_vector: Point) -> float:
		"""Calculate angle between wall and another vector in degrees"""
		dot = self.vector.x * other_vector.x + self.vector.y * other_vector.y
		norms = self.length * sqrt(other_vector.x * other_vector.x + other_vector.y * other_vector.y)
		cos_angle = dot / norms if norms != 0 else 0
		cos_angle = min(1.0, max(-1.0, cos_angle))  # Handle numerical errors
		angle = acos(cos_angle) * 180 / pi
		return angle
	
	def reverse(self):
		"""Switch places of start and end points"""
		if self.start == self.end:
			return self
		return Wall(self.end, self.start)
	
	def __eq__(self, other):
		"""Overload equality operator to compare walls"""
		if not isinstance(other, Wall):
			return False
		return self.start == other.start and self.end == other.end and self.wall_type == other.wall_type
	
	def __hash__(self):
		"""Overload hash operator to use walls in sets"""
		return hash((self.start, self.end, self.wall_type))



class Room:
	def __init__(self, corners: list[Point]):
		self.corners = corners
		# Calculate center as average of x and y coordinates
		center_x = sum(corner.x for corner in corners) / len(corners)
		center_y = sum(corner.y for corner in corners) / len(corners)
		self.center = Point(center_x, center_y)
		self.walls = self._create_walls()
	
	def _create_walls(self) -> List[Wall]:
		walls = []
		for i in range(len(self.corners)):
			start = self.corners[i]
			end = self.corners[(i + 1) % len(self.corners)]
			walls.append(Wall(start, end))
		return walls


class FloorPlan:
	def __init__(self, rooms: list[Room] = None, ahu: AirHandlingUnit = None):
		self.walls = []
		self._rooms = []
		self.ahu = None  # Initialize as None by default
		if rooms is not None:
			self.add_rooms(rooms)
		if ahu is not None:
			self.ahu = ahu

	def add_room(self, room):
		self._rooms.append(room)
		self.update_walls()

	def update_walls(self):
		unique_walls = set()
		for room in self._rooms:
			for wall in room.walls:
				reverse_wall = wall.reverse()
				if wall not in unique_walls and reverse_wall not in unique_walls:
					unique_walls.add(wall)
		self.walls = list(unique_walls)

	

	def add_rooms(self, rooms):
		for room in rooms:
			self.add_room(room)



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
        # Check if path crosses wall
        if line_intersection(current, next, self.wall.start, self.wall.end):
            path_vector = Point(next.x - current.x, next.y - current.y)
            angle = self.wall.get_angle_with(path_vector)
            angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
            return self.perpendicular_cost if abs(90 - angle) <= 3 else self.angled_cost
        
        # If not crossing, check proximity
        current_dist = point_to_line_distance(current, self.wall.start, self.wall.end)
        next_dist = point_to_line_distance(next, self.wall.start, self.wall.end)
        
        min_dist = min(current_dist, next_dist)
        if min_dist >= WallCosts.PROXIMITY_THRESHOLD:
            return 0.0
        
        # Linear interpolation between 0 and perpendicular_cost based on distance
        return self.perpendicular_cost * (1 - min_dist / WallCosts.PROXIMITY_THRESHOLD)
