from datetime import datetime
from typing import List

import numpy as np
from structural import Room, Wall, FloorPlan, WallType
from core import Node, Cost
from queue import PriorityQueue
import matplotlib.pyplot as plt
from geometry import Line, Point, Vector
from abc import ABC, abstractmethod
from math import sqrt

class MovementCost(Cost):
	def calculate(self, current: Point, next: Point) -> float:
		# dx = abs(next.x - current.x)
		# dy = abs(next.y - current.y)
		# # Use Euclidean distance for more accurate diagonal costs
		# return sqrt(dx * dx + dy * dy)
		return current.distanceTo(next)

class WallCost(Cost):
	"""Central definition of wall-related costs"""
	PROXIMITY_THRESHOLD = 0.5  # Distance at which wall proximity starts affecting cost
	ANGLE_TOLERANCE = 2 # Degrees of tolerance in angle calculations
	
	def __init__(self, wall: Wall, costWeights: dict[str, float]):
		self.wall = wall
		self.costWeights = costWeights
		self._pathVector = None
		self._pathSegment = None
		self._baseCost = self._getBaseCost(self.wall.wallType)

	@staticmethod
	def _getBaseCost(wallType: WallType) -> float:
		"""Get the base perpendicular crossing cost for a wall type"""
		if wallType == WallType.DRYWALL:
			return 1.0
		elif wallType == WallType.CONCRETE:
			return 50.0
		else:  # OUTER_WALL
			return 200.0

	def calculate(self, current: Point, next: Point) -> float:
		self._pathVector=next-current
		self._pathSegment = Line(current, next)
		if self._pathSegment.intersects(self.wall):
			# Through a wall
			angle = self._pathVector.getAngleWith(self.wall.vector)
			angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
			if abs(90-angle) <= self.ANGLE_TOLERANCE:
				#Handles perpendicular wall crossings (90° ± tolerance°)
				return self._baseCost*self.costWeights["perpendicularWallCrossing"]
			else:
				# Angled wall crossing
				return self._baseCost*self.costWeights["angledWallCrossing"]
			
		else:
			# Not through a wall, but maybe close?
			proximityToWall = min(current.distanceTo(self.wall),next.distanceTo(self.wall))
			if proximityToWall < self.PROXIMITY_THRESHOLD:
				# Close to a wall, but not through it
				return self._baseCost* self.costWeights["wallProximity"]
		
			else:
				# Not close to a wall, no cost
				return 0

	
class SoundRatingCost(Cost):
	def __init__(self, floorPlan: FloorPlan):
		self.floorPlan = floorPlan
		self._maxSoundRating = 70
	
	def calculate(self, current: Point, next: Point) -> float:
		for room in self.floorPlan.rooms:
			if room.isInsideRoom(next):
				distance = current.distanceTo(next)
				return (self._maxSoundRating-room.soundRating)*distance
		else:
			return 0

class CompositeCost(Cost):
	def __init__(self, costs: List[Cost]):
		self.costs = costs  # List of costs
	
	def calculate(self, current: Point, next: Point) -> float:
		return sum(cost.calculate(current, next) for cost in self.costs)

class Heuristic(ABC):
	@abstractmethod
	def calculate(self, current: Point, destination: Point) -> float:
		pass

class EnhancedDistance(Heuristic):
	def __init__(self, floor_plan: FloorPlan):
		self.floorPlan = floor_plan
		
	def _estimate_wall_cost(self, current: Point, destination: Point) -> float:
		"""Estimate minimum wall crossing costs to destination"""
		distance = (destination-current).length
		if distance == 0:
			return 0
		
		# Count wall crossings along direct path
		min_cost = 0
		for wall in self.floorPlan.walls:
			if Line(wall.start, wall.end).intersects(Line(current, destination)):
				# Use base cost as minimum (perpendicular crossing)
				min_cost += WallCost._getBaseCost(wall.wallType)
		
		return min_cost
			
	def calculate(self, current: Point, destination: Point) -> float:
		# Base distance
		distance = (destination-current).length
		# Add minimum wall crossing costs
		wall_cost = self._estimate_wall_cost(current, destination)
		return distance + wall_cost

class SoundRatingHeuristic(SoundRatingCost):
	def __init__(self, floorPlan: FloorPlan):
		super().__init__(floorPlan)

class CompositeHeuristic(Heuristic):
	def __init__(self, heuristics: List[Heuristic]):
		self.heuristics = heuristics  # List of heuristics
		
	def calculate(self, current: Point, destination: Point) -> float:
		return sum(h.calculate(current, destination) for h in self.heuristics)

class Pathfinder:
	def __init__(self, floor_plan: FloorPlan,vizualiser=None, startTime: datetime=None):
		self.floor_plan = floor_plan
		self._init_costs()
		self.composite_h = CompositeHeuristic([EnhancedDistance(self.floor_plan)
										 ,SoundRatingHeuristic(self.floor_plan)])
		self.open_list = None
		self.path = None
		self._visualizer = vizualiser
		self.startTime = startTime
		self.TOLERANCE = 1
		self.MAX_ITERATIONS = 5000
		self.MINIMUM_STEP_SIZE = 1
		self.costWeights={
			"distance":1,
			"wallProximity":1,
			"perpendicularWallCrossing":1,
			"angledWallCrossing":200,
			"soundRating":1.5
		}
		self._steps = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]

	
	def _get_nearby_walls(self, position: Point, radius: float = 5.0) -> List[Wall]:
		"""Get walls within specified radius of position"""
		return [wall for wall in self.floor_plan.walls 
				if min(position.distanceTo(wall.start), 
						position.distanceTo(wall.end)) <= radius]

	def _init_costs(self):
		"""Initialize cost functions with movement as primary cost"""
		self.movement_cost = MovementCost()
		self.soundRatingCost = SoundRatingCost(self.floor_plan)
		
	def _calculate_cost(self, current: Point, next: Point) -> tuple[float, bool]:
		"""Calculate total cost considering only nearby walls"""
		# Base movement cost
		total_cost = 0
		movementCost = self.costWeights["distance"]*self.movement_cost.calculate(current, next)
		closeToWall = False
		# Get nearby walls and calculate their costs
		nearby_walls = self._get_nearby_walls(current)
		for wall in nearby_walls:
			wallCost = WallCost(wall,self.costWeights)
			if wallCost:
				closeToWall = True
			total_cost += wallCost.calculate(current, next)
		
		# Calculate cost of movement inside a room with sound rating
		sound_cost = self.costWeights["soundRating"]*self.soundRatingCost.calculate(current, next)
		total_cost += sound_cost

		return (total_cost, closeToWall)

	def a_star(self, start: Point, target: Point, viz = None):
	
		"""Find shortest path between start_pos and destination_pos using A* algorithm.
		
		Args:
			start_pos: Point providing coordinates for starting position.
			target_pos: Point providing coordinates for target position.
			
		Returns:
			List of Node representing shortest path, or empty list if no path found
		"""
		if viz:
			self._visualizer = viz
		start_node = Node(start)
		end_node = Node(target)
		
		# Priority queue for nodes to explore, ordered by f_score (g_score + heuristic)
		self.open_list = PriorityQueue()
		self.open_list.put((0, start_node))
		
		# Set to track nodes already evaluated
		closed_set = set()
		
		iterations = 0
		stepSize = 2.5
		highestRegisteredStepSize = stepSize

		while not self.open_list.empty() and iterations < self.MAX_ITERATIONS:
			iterations += 1
			_, current_node = self.open_list.get()
			
			# Check if already processed
			current_pos_rounded = (round(current_node.position.x + 1e-10), round(current_node.position.y + 1e-10))
			if current_pos_rounded in closed_set:
				continue

			if current_node.position.distanceTo(end_node.position) < self.TOLERANCE:
				path = []
				node = current_node  # Use a separate variable to build path
				while node:
					path.insert(0,node)
					node = node.parentNode
				print(f"Path found in {iterations} iterations")
				self.path = path
				if self._visualizer is not None:
					# Update visualization one last time
					self._visualizer.update_node(current_node, current_node.position)
					self._visualizer.update_path()
					plt.pause(1)  # Final pause to show the complete path
				return
			elif current_node.position.distanceTo(end_node.position) < stepSize:
				stepSize = self.MINIMUM_STEP_SIZE
			
			# Add to closed set after destination check
			closed_set.add(current_pos_rounded)
			currentSteps = []
			for step in self._steps:
				dx, dy = step
				dx = dx*stepSize
				dy = dy*stepSize
				currentSteps.append((dx,dy))

			inflencedByWalls = []
			for dx, dy in currentSteps:
				neighbor_pos = current_node.position + Vector(dx,dy)
				neighbor_pos_rounded = Point(round(neighbor_pos.x + 1e-10), round(neighbor_pos.y + 1e-10))
				
				if neighbor_pos_rounded in closed_set:
					continue
				
				neighbor = Node(neighbor_pos, current_node)
				
				# Calculate g cost using our optimized cost calculation
				
				(g_cost, inflencedByWall) = self._calculate_cost(current_node.position, neighbor_pos)
				inflencedByWalls.append(inflencedByWall)
				neighbor.g_cost = current_node.g_cost + g_cost
				
				# Calculate h cost using provided heuristic
				neighbor.h = self.composite_h.calculate(neighbor_pos, end_node.position)
				neighbor.f = neighbor.g_cost + neighbor.h
				
				self.open_list.put((neighbor.f, neighbor))
				
				# if self._visualizer is not None:
				# 	# Update visualization
				# 	self._visualizer.update_node(current_node, current_node.position)
				# 	# Add a longer pause every 10 iterations, otherwise use a small pause
				# 	plt.pause(0.000001)
			
			if sum(inflencedByWalls): # If close to at least one wall, decrease step size. It not, increase
				stepSize = self.MINIMUM_STEP_SIZE
			else:
				stepSize += 0.5
				if stepSize > highestRegisteredStepSize:
					highestRegisteredStepSize = stepSize
			if iterations % 100 == 0:
				print(f"Iteration {iterations}, current position: {current_node.position}, destination: {target}")
		
		print(f"No path found from {start} to {target} after {iterations} iterations")
		return

	def create_direct_route(self, start: Point, end: Point) -> List[Point]:
		self.path = [start, end]
		return

	def __len__(self) -> float:
		return len(self.path)