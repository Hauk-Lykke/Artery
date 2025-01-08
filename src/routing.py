from core import Node
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue
from structural import FloorPlan
from pathfinding import Pathfinder
from visualization import PathfindingVisualizer, visualize_layout


class Path:
	'''Class for storing Mechanical, Electrical and Plumbing routes. Each bend/fitting is a node.'''
	def __init__(self, startNode: Node, goal: Node=None):
		self.startNode = startNode
		self.endNode = None
		self.nodes = [startNode]
		self.length = 0
		self.cost = self.nodes[-1].g
		self.goal = goal
	
	def maxCost(self) -> float:
		# Create a copy to avoid modifying original list
		nodesSortedByCost = self.nodes.copy()
		# Fix lambda syntax and sort in descending order
		nodesSortedByCost.sort(key=lambda x: x.g_cost, reverse=True)
		# Return the highest cost (first element)
		return nodesSortedByCost[0].g_cost if nodesSortedByCost else 0

	def append(self, node: Node):
		self.nodes.append(node)
		self.startNode = node

	def __getitem__(self,index: int) -> Node:
		return self.nodes[index]

class Branch(Path): # Mechanical, Electrical, Plumbing branch
	def __init__(self, startNode: Node, isIndexRoute: bool = False):
		super().__init__(startNode)
		self.sub_branches = []
		self.isIndexRoute = isIndexRoute

class Branch2D(Path):
	def __init__(self, floorPlan: FloorPlan, startNode: Node, isIndexRoute: bool = False):
		super().__init__(startNode, isIndexRoute)
		self.floorPlan = floorPlan
		self.figure = None # Figure handle
		self.axes = None # Figure axes

	def generate(self):
		if self.floorPlan.ahu is None:
			raise ValueError("AHU must be set in floor plan before routing ducts")

		self.pathfinder = Pathfinder(self.floorPlan)
		furthest_room = self.pathfinder.find_furthest_room(self.floorPlan.ahu)
		self.goal = furthest_room.center

		print(f"AHU position: {self.floorPlan.ahu.position}")
		print(f"Furthest room center: {furthest_room.center}")
		# Create route to the furthest room using optimized A* pathfinding
		self.nodes = self.pathfinder.a_star(self.floorPlan.ahu.position, furthest_room.center, ax=self.axes)
	
	def visualize(self, test_name: str=None):
		self.fig, self.ax = plt.subplots(figsize=(12, 8))
		visualize_layout(self.floorPlan, self.ax)
		visualizer = PathfindingVisualizer(self.pathfinder, self.ax)
		# If open list is empty, algorithm has completed
		if not visualizer.pathfinder.open_list:
			if visualizer.open_list.queue and test_name:
				visualizer.save_figure(test_name)(self, self.ax)
		plt.draw()
		plt.show(block=True)  # This will keep the window open even if the test fails
		return
