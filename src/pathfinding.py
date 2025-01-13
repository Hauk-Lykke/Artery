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
	def calculate(self, current: Point, destination: Point) -> float:
		pass

class EnhancedDistance(Heuristic):
	def __init__(self, floor_plan: FloorPlan):
		self.floor_plan = floor_plan
		
	def _estimate_wall_cost(self, current: Point, destination: Point) -> float:
		"""Estimate minimum wall crossing costs to destination"""
		distance = (destination-current).length
		if distance == 0:
			return 0
		
		# Count wall crossings along direct path
		min_cost = 0
		for wall in self.floor_plan.walls:
			if Line(wall.start, wall.end).intersects(Line(current, destination)):
				# Use base cost as minimum (perpendicular crossing)
				min_cost += WallCosts.get_base_cost(wall.wall_type)
		
		return min_cost
			
	def calculate(self, current: Point, destination: Point) -> float:
		# Base distance
		distance = (destination-current).length
		# Add minimum wall crossing costs
		wall_cost = self._estimate_wall_cost(current, destination)
		return distance + wall_cost

class CompositeHeuristic(Heuristic):
	def __init__(self, heuristics: List[Heuristic]):
		self.heuristics = heuristics  # List of heuristics
		
	def calculate(self, current: Point, destination: Point) -> float:
		return sum(h.calculate(current, destination) for h in self.heuristics)

class Pathfinder:
	def __init__(self, floor_plan: FloorPlan,vizualiser=None):
		self.floor_plan = floor_plan
		self._init_costs()
		self.composite_h = CompositeHeuristic([EnhancedDistance(floor_plan)])
		self.open_list = None
		self.path = None
		self._visualizer = vizualiser
		self.TOLERANCE = 1
		self.MAX_ITERATIONS = 5000
	
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
			
			# Add to closed set after destination check
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
				
				# if self._visualizer is not None:
				# 	# Update visualization
				# 	self._visualizer.update_node(current_node, current_node.position)
				# 	# Add a longer pause every 10 iterations, otherwise use a small pause
				# 	plt.pause(0.000001)
			
			if iterations % 100 == 0:
				print(f"Iteration {iterations}, current position: {current_node.position}, destination: {target}")
		
		print(f"No path found from {start} to {target} after {iterations} iterations")
		return

	def create_direct_route(self, start: Point, end: Point) -> List[Point]:
		self.path = [start, end]
		return

	def __len__(self) -> float:
		return len(self.path)