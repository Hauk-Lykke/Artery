from typing import List
from structural import Room, Wall, FloorPlan
from core import Node, Cost
from queue import PriorityQueue
import matplotlib.pyplot as plt
from structural import StandardWallCost, WallCosts
from geometry import Line, Point, Vector
from abc import ABC, abstractmethod
from math import sqrt

class MovementCost(Cost):
	def calculate(self, current: Point, next: Point) -> float:
		dx = abs(next.x - current.x)
		dy = abs(next.y - current.y)
		# Use Euclidean distance for more accurate diagonal costs
		return sqrt(dx * dx + dy * dy)

class CompositeCost(Cost):
	def __init__(self, costs: List[Cost]):
		self.costs = costs  # List of costs
	
	def calculate(self, current: Point, next: Point) -> float:
		return sum(cost.calculate(current, next) for cost in self.costs)

class Heuristic(ABC):
	@abstractmethod
	def calculate(self, current: Point, goal: Point) -> float:
		pass

class EnhancedDistance(Heuristic):
	def __init__(self, floor_plan: FloorPlan):
		self.floor_plan = floor_plan
		
	def _estimate_wall_cost(self, current: Point, goal: Point) -> float:
		"""Estimate minimum wall crossing costs to goal"""
		distance = (goal-current).length
		if distance == 0:
			return 0
		
		# Count wall crossings along direct path
		min_cost = 0
		for wall in self.floor_plan.walls:
			if Line(wall.start, wall.end).intersects(Line(current, goal)):
				# Use base cost as minimum (perpendicular crossing)
				min_cost += WallCosts.get_base_cost(wall.wall_type)
		
		return min_cost
			
	def calculate(self, current: Point, goal: Point) -> float:
		# Base distance
		distance = (goal-current).length
		# Add minimum wall crossing costs
		wall_cost = self._estimate_wall_cost(current, goal)
		return distance + wall_cost

class CompositeHeuristic(Heuristic):
	def __init__(self, heuristics: List[Heuristic]):
		self.heuristics = heuristics  # List of heuristics
		
	def calculate(self, current: Point, goal: Point) -> float:
		return sum(h.calculate(current, goal) for h in self.heuristics)

class Pathfinder:
	def __init__(self, floor_plan: FloorPlan, vizualiser=None):
		self.floor_plan = floor_plan
		self._init_costs()
		self.composite_h = CompositeHeuristic([EnhancedDistance(floor_plan)])
		self.open_list = None
		self.path = None
		self._visualizer = vizualiser
	
	def _get_nearby_walls(self, position: Point, radius: float = 5.0) -> List[Wall]:
		"""Get walls within specified radius of position"""
		return [wall for wall in self.floor_plan.walls 
				if min(position.distanceTo(wall.start), 
						position.distanceTo(wall.end)) <= radius]

	def _init_costs(self):
		"""Initialize cost functions with movement as primary cost"""
		self.movement_cost = MovementCost()
		
	def _calculate_cost(self, current: Point, next: Point) -> float:
		"""Calculate total cost considering only nearby walls"""
		# Base movement cost
		total_cost = self.movement_cost.calculate(current, next)
		
		# Get nearby walls and calculate their costs
		nearby_walls = self._get_nearby_walls(current)
		for wall in nearby_walls:
			wall_cost = StandardWallCost(wall)
			total_cost += wall_cost.calculate(current, next)
		
		return total_cost
	
	def findFurthestRoom(self, start: Point) -> Room:
		if not isinstance(start, Point):
			raise ValueError("Start must be a Point.")
		if not self.floor_plan._rooms:
			raise ValueError("Floor plan must have rooms before finding furthest room")
		return max(self.floor_plan._rooms, key=lambda room: room.center.distanceTo(start))

	def a_star(self, start: Point, goal: Point, viz = None):
		if viz:
			self._visualizer = viz
		start_node = Node(start)
		self.path = [start_node]
		end_node = Node(goal)
		
		self.open_list = PriorityQueue()
		self.open_list.put((0, start_node))
		closed_set = set()
		
		iterations = 0
		max_iterations = 1000
		
		while not self.open_list.empty() and iterations < max_iterations:
			iterations += 1
			_, current_node = self.open_list.get()
			
			# Check if already processed
			current_pos_rounded = (round(current_node.position.x + 1e-10), round(current_node.position.y + 1e-10))
			if current_pos_rounded in closed_set:
				continue

			if current_node.position.distanceTo(end_node.position) < 0.5:
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
					plt.pause(1)  # Final pause to show the complete path
				path.reverse()
				self.path = path
				return
			
			# Add to closed set after goal check
			closed_set.add(current_pos_rounded)

			for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
				neighbor_pos = current_node.position + Vector(dx,dy)
				neighbor_pos_rounded = Point(round(neighbor_pos.x + 1e-10), round(neighbor_pos.y + 1e-10))
				
				if neighbor_pos_rounded in closed_set:
					continue
				
				neighbor = Node(neighbor_pos, current_node)
				
				# Calculate g cost using our optimized cost calculation
				g_cost = self._calculate_cost(current_node.position, neighbor_pos)
				neighbor.g_cost = current_node.g_cost + g_cost
				
				# Calculate h cost using provided heuristic
				neighbor.h = self.composite_h.calculate(neighbor_pos, end_node.position)
				neighbor.f = neighbor.g_cost + neighbor.h
				
				self.open_list.put((neighbor.f, neighbor))
				
				if self._visualizer is not None:
					# Update visualization
					self._visualizer.update_node(current_node, current_node.position)
					# Add a longer pause every 10 iterations, otherwise use a small pause
					plt.pause(0.001 if iterations % 10 == 0 else 0.0001)
			
			if iterations % 100 == 0:
				print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
		
		print(f"No path found from {start} to {goal} after {iterations} iterations")
		return

	def create_direct_route(self, start: Point, end: Point) -> List[Point]:
		self.path = [start, end]
		return

	def __len__(self) -> float:
		return len(self.path)