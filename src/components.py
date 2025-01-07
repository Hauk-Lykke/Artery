import numpy as np
from typing import List, Tuple
from src.geometry import Point
from math import sqrt, acos, pi

class Building:
		def __init__(self):
			self.floor_plans = []


class AirHandlingUnit:
	def __init__(self, position: Point):
		self.position = position

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
	def __init__(self, corners: List[Point]):
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
	def __init__(self, rooms: List[Room] = None, ahu: AirHandlingUnit = None):
		self.walls = []
		self._rooms = []
		self.ahu = None  # Initialize as None by default
		if rooms is not None:
			self.add_rooms(rooms)
		if ahu is not None:
			self.ahu = ahu

	def update_walls(self):
		unique_walls = set()
		for room in self._rooms:
			for wall in room.walls:
				test_wall = wall
				if wall not in unique_walls and wall.reverse() not in unique_walls:
					unique_walls.add(wall)
		self.walls = list(unique_walls)

	def add_room(self, room):
		self._rooms.append(room)
		self.update_walls()

	def add_rooms(self, rooms):
		for room in rooms:
			self.add_room(room)

