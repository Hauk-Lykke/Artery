import numpy as np
from typing import List, Tuple
from src.core import Cost

class Building:
		def __init__(self):
			self.floor_plans = []

class FloorPlan:
	def __init__(self):
		self._rooms = []
		self.ahu = None
		self.walls = []
		self.update_walls()

	def update_walls(self):
		self.walls = []
		for room in self._rooms:
			self.walls.extend(room.walls)

	def add_room(self, room):
		self._rooms.append(room)
		self.walls.extend(room.walls)

	def add_rooms(self, rooms):
		for room in rooms:
			self.add_room(room)
		self.update_walls()

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
		self.wall_crossing_cost = WallProximityCost(self)
		
		
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
	

class AHU:
	def __init__(self, position: Tuple[float, float]):
		self.position = np.array(position)

class WallProximityCost(Cost):
	PROXIMITY_THRESHOLD = 1.0  # Distance at which wall proximity starts affecting cost
	
	def __init__(self, wall: Wall):
		self.wall = wall
		if wall.wall_type == WallType.DRYWALL:
			self.perpendicular_cost = 1.0
		elif wall.wall_type == WallType.CONCRETE:
			self.perpendicular_cost = 3.0
		else:
			self.perpendicular_cost = 8.0
		self.angled_cost = 2*self.perpendicular_cost
	
	def _line_intersection(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> bool:
		"""Check if line segments (p1,p2) and (p3,p4) intersect."""
		def ccw(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
			val = (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
			if abs(val) < 1e-10:  # Points are collinear
				return False
			return val > 0
		return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))
	
	def _point_to_line_distance(self, point: np.ndarray) -> float:
		"""Calculate the shortest distance from a point to the wall segment"""
		wall_vec = self.wall.vector
		wall_len_sq = np.dot(wall_vec, wall_vec)
		if wall_len_sq == 0:
			return np.linalg.norm(point - self.wall.start)
		
		t = max(0, min(1, np.dot(point - self.wall.start, wall_vec) / wall_len_sq))
		projection = self.wall.start + t * wall_vec
		return np.linalg.norm(point - projection)
	
	def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
		# Check if path crosses wall
		if self._line_intersection(current, next, self.wall.start, self.wall.end):
			path_vector = next - current
			angle = self.wall.get_angle_with(path_vector)
			angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
			return self.perpendicular_cost if abs(90 - angle) <= 3 else self.angled_cost
		
		# If not crossing, check proximity
		current_dist = self._point_to_line_distance(current)
		next_dist = self._point_to_line_distance(next)
		
		min_dist = min(current_dist, next_dist)
		if min_dist >= self.PROXIMITY_THRESHOLD:
			return 0.0
		
		# Linear interpolation between 0 and angled_cost based on distance
		return self.perpendicular_cost * (1 - min_dist / self.PROXIMITY_THRESHOLD)
