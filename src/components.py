import numpy as np
from typing import List, Tuple

class Building:
		def __init__(self):
			self.floor_plans = []


class AirHandlingUnit:
	def __init__(self, position: Tuple[float, float]):
		self.position = np.array(position)

class WallType:
	'''Enum class for wall types'''
	DRYWALL = 1
	CONCRETE = 2
	OUTER_WALL = 3

class Wall:
	def __init__(self, startpoint: Tuple[float, float], endpoint: Tuple[float, float], wall_type: WallType = WallType.DRYWALL):
		self.start = np.array(startpoint)
		self.end = np.array(endpoint)
		self._vector = self.end - self.start
		self.wall_type = wall_type
	@property
	def vector(self) -> np.ndarray:
		"""Get wall direction vector"""
		return self._vector
	
	@property
	def length(self) -> float:
		"""Get wall length"""
		return np.linalg.norm(self.vector)
	
	def get_angle_with(self, other_vector: np.ndarray) -> float:
		"""Calculate angle between wall and another vector in degrees"""
		dot = np.dot(self.vector, other_vector)
		norms = np.linalg.norm(self.vector) * np.linalg.norm(other_vector)
		cos_angle = dot / norms if norms != 0 else 0
		cos_angle = min(1.0, max(-1.0, cos_angle))  # Handle numerical errors
		angle = np.arccos(cos_angle) * 180 / np.pi
		return angle



class Room:
	def __init__(self, corners: List[Tuple[float, float]]):
		self.corners = np.array(corners)
		self.center = np.mean(corners, axis=0)
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
		self.walls = []
		for room in self._rooms:
			self.walls.extend(room.walls)

	def add_room(self, room):
		self._rooms.append(room)
		self.update_walls()

	def add_rooms(self, rooms):
		for room in rooms:
			self.add_room(room)
