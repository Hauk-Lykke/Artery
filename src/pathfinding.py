from typing import List, Tuple, Protocol
import numpy as np
from structural import Room, Wall, FloorPlan
from MEP import AirHandlingUnit
from core import Node, Cost
from queue import PriorityQueue
import matplotlib.pyplot as plt
from visualization import PathfindingVisualizer
from structural import StandardWallCost, WallCosts
from routing import Branch
from geometry import line_intersection, Point
from abc import ABC, abstractmethod
from math import atan2, pi, sqrt

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
		distance = len(goal-current)
		if distance == 0:
			return 0
		
		# Count wall crossings along direct path
		min_cost = 0
		for wall in self.floor_plan.walls:
			if line_intersection(current, goal, wall.start, wall.end):
				# Use base cost as minimum (perpendicular crossing)
				min_cost += WallCosts.get_base_cost(wall.wall_type)
		
		return min_cost
			
	def calculate(self, current: Point, goal: Point) -> float:
		# Base distance
		distance = self.len(goal-current)
		# Add minimum wall crossing costs
		wall_cost = self._estimate_wall_cost(current, goal)
		return distance + wall_cost

class CompositeHeuristic(Heuristic):
	def __init__(self, heuristics: List[Heuristic]):
		self.heuristics = heuristics  # List of heuristics
		
	def calculate(self, current: Point, goal: Point) -> float:
		return sum(h.calculate(current, goal) for h in self.heuristics)

class Pathfinder:
	def __init__(self, floor_plan: FloorPlan, branch: Branch):
		self.floor_plan = floor_plan
		self._init_costs()
		self.composite_h = CompositeHeuristic([EnhancedDistance(floor_plan)])
		self.open_list = None
		self.nodes = None
	
	def _get_nearby_walls(self, position: Point, radius: float = 5.0) -> List[Wall]:
		"""Get walls within specified radius of position"""
		return [wall for wall in self.floor_plan.walls 
				if min(self.between_points(position, wall.start), 
						self.between_points(position, wall.end)) <= radius]

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
	
	def find_furthest_room(self, ahu: AirHandlingUnit) -> Room:
		if ahu is None:
			raise ValueError("AHU must be set in floor plan before finding furthest room")
		if not self.floor_plan._rooms:
			raise ValueError("Floor plan must have rooms before finding furthest room")
		ahu_pos = ahu.position
		return max(self.floor_plan._rooms, key=lambda room: self.between_points(
			room.center, ahu_pos))

	def a_star(self, start: Point, goal: Point, ax=None):
			
		start_node = Node(start)
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

			if self.between_points(current_node.position, end_node.position) < 0.5:
				path = []
				costs = []
				node = current_node  # Use a separate variable to build path
				while node:
					path.append(node)
					node = node.parent
				print(f"Path found in {iterations} iterations")
				if ax and hasattr(ax, '_visualizer'):
					# Update visualization one last time
					ax._visualizer.update_node(current_node, current_node.position, self.open_list)
					plt.pause(1)  # Final pause to show the complete path
				self.nodes = path
				return
			
			# Add to closed set after goal check
			closed_set.add(current_pos_rounded)

			for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
				neighbor_pos = Point(current_node.position.x + dx, current_node.position.y + dy)
				neighbor_pos_rounded = Point(round(neighbor_pos.x + 1e-10), round(neighbor_pos.y + 1e-10))
				
				if neighbor_pos_rounded in closed_set:
					continue
				
				neighbor = Node(neighbor_pos, current_node)
				
				# Calculate g cost using our optimized cost calculation
				g_cost = self._calculate_cost(current_node.position, neighbor_pos)
				neighbor.g = current_node.g + g_cost
				
				# Calculate h cost using provided heuristic
				neighbor.h = self.composite_h.calculate(neighbor_pos, end_node.position)
				neighbor.f = neighbor.g + neighbor.h
				
				self.open_list.put((neighbor.f, neighbor))
				
				if ax:
					if not hasattr(ax, '_visualizer'):
						ax._visualizer = PathfindingVisualizer(ax)
					ax._visualizer.update_node(current_node, neighbor_pos, self.open_list)
					# Add a longer pause every 10 iterations, otherwise use a small pause
					plt.pause(0.001 if iterations % 10 == 0 else 0.0001)
			
			if iterations % 100 == 0:
				print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
		
		print(f"No path found from {start} to {goal} after {iterations} iterations")
		return [], []

	def create_direct_route(self, start: Point, end: Point) -> List[Point]:
		self.nodes = [start, end]
		return
