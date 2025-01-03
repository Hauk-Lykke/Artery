from typing import List, Tuple, Protocol
import numpy as np
from src.components import Room, Wall, AHU, FloorPlan
from src.core import Node, Cost
from queue import PriorityQueue
import matplotlib.pyplot as plt
from src.structural import StandardWallCost
from abc import ABC, abstractmethod
from math import atan2, pi

class MovementCost(Cost):
	def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
		diff = np.abs(current - next)
		# Use Euclidean distance for more accurate diagonal costs
		return np.sqrt(np.sum(diff * diff))

class CompositeCost(Cost):
	def __init__(self, costs: List[Cost]):
		self.costs = costs  # List of costs
	
	def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
		return sum(cost.calculate(current, next) for cost in self.costs)

class Heuristic(ABC):
	@abstractmethod
	def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
		pass

class EuclideanDistance(Heuristic):
	@staticmethod
	def between_points(a: np.ndarray, b: np.ndarray) -> float:
		"""Calculate Euclidean distance between two points"""
		diff = np.abs(a - b)
		return np.sqrt(np.sum(diff * diff))
		
	def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
		return self.between_points(current, goal)

class CompositeHeuristic(Heuristic):
	def __init__(self, heuristics: List[Heuristic]):
		self.heuristics = heuristics  # List of heuristics
		
	def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
		return sum(h.calculate(current, goal) for h in self.heuristics)

class Pathfinder:
	def __init__(self, floor_plan: FloorPlan):
		self.floor_plan = floor_plan
		self._init_costs()
		self.composite_h = CompositeHeuristic([EuclideanDistance()])
	
	def _init_costs(self):
		"""Initialize cost functions with movement as primary and reduced wall costs"""
		# Start with movement cost
		costs = [MovementCost()]
		
		# Add wall costs
		for wall in self.floor_plan.walls:
			costs.append(StandardWallCost(wall))
		
		self.composite_cost = CompositeCost(costs)
	
	def find_furthest_room(self, ahu: AHU) -> Room:
		return max(self.floor_plan._rooms, key=lambda room: EuclideanDistance.between_points(room.center, ahu.position))

	def a_star(self, start: np.ndarray, goal: np.ndarray, 
			   heuristic: Heuristic = None, cost: Cost = None, ax=None) -> Tuple[List[np.ndarray], List[float]]:
		if heuristic is None:
			heuristic = self.composite_h
		if cost is None:
			cost = self.composite_cost
			
		start_node = Node(start)
		end_node = Node(goal)
		
		open_list = PriorityQueue()
		open_list.put((0, start_node))
		closed_set = set()
		
		iterations = 0
		max_iterations = 1000
		
		while not open_list.empty() and iterations < max_iterations:
			iterations += 1
			current_node = open_list.get()[1]
			
			if np.allclose(current_node.position, end_node.position, atol=0.5):
				path = []
				costs = []
				while current_node:
					path.append(current_node.position)
					costs.append(current_node.g)
					current_node = current_node.parent
				print(f"Path found in {iterations} iterations")
				return path[::-1], costs[::-1]
			
			# Add small offset before rounding to handle floating point imprecision
			closed_pos = tuple(map(lambda x: round(x + 1e-10), current_node.position))
			closed_set.add(closed_pos)
			
			for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
				neighbor_pos = current_node.position + np.array([dx, dy])
				neighbor_pos_rounded = tuple(map(lambda x: round(x + 1e-10), neighbor_pos))
				
				if neighbor_pos_rounded in closed_set:
					continue
				
				neighbor = Node(neighbor_pos, current_node)
				
				# Calculate g cost using provided cost function
				g_cost = cost.calculate(current_node.position, neighbor_pos)
				neighbor.g = current_node.g + g_cost
				
				# Calculate h cost using provided heuristic
				neighbor.h = heuristic.calculate(neighbor_pos, end_node.position)
				neighbor.f = neighbor.g + neighbor.h
				
				open_list.put((neighbor.f, neighbor))
				
				if ax:
					# Initialize colorbar if not already done
					if not hasattr(ax, '_cost_mapper'):
						ax._cost_mapper = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=0, vmax=1))
						ax._colorbar = plt.colorbar(ax._cost_mapper, ax=ax, label='Path Cost')
						# Store initial axis limits
						ax._xlim = ax.get_xlim()
						ax._ylim = ax.get_ylim()
					
					# Update the maximum cost seen so far
					current_max_cost = max(neighbor.g for _, neighbor in list(open_list.queue) + [(0, current_node)])
					
					# Update normalization for colorbar
					ax._cost_mapper.norm.vmax = current_max_cost
					
					# Color the attempted nodes based on cost relative to current maximum
					normalized_cost = neighbor.g / current_max_cost if current_max_cost > 0 else 0
					color = plt.cm.viridis(normalized_cost)
					ax.plot(neighbor_pos[0], neighbor_pos[1], 'o', color=color, markersize=2)
					
					# Restore axis limits
					ax.set_xlim(ax._xlim)
					ax.set_ylim(ax._ylim)
					
					# Update colorbar
					ax._colorbar.update_normal(ax._cost_mapper)
					
					# Add a longer pause every 10 iterations, otherwise use a small pause
					plt.pause(0.1 if iterations % 10 == 0 else 0.001)
			
			if iterations % 100 == 0:
				print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
		
		print(f"No path found from {start} to {goal} after {iterations} iterations")
		return [], []

	def create_direct_route(self, start: np.ndarray, end: np.ndarray) -> List[np.ndarray]:
		return [start, end]
