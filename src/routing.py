from typing import List, Union
from core import Node
import matplotlib.pyplot as plt
from structural import FloorPlan
from pathfinding import Pathfinder
from geometry import Point
from visualization import PathfindingVisualizer

class Path:
	'''Class for storing Mechanical, Electrical and Plumbing routes. Each bend/fitting is a node.'''
	def __init__(self, startNode: Union[Node,Point,List[Node]]): # Union[float, Tuple[float, float, float]] 
		if isinstance(startNode, Node):
			self.startNode = startNode
			self.nodes = [self.startNode]
		if isinstance(startNode, list):
			self.nodes = startNode
			if len(startNode):
				self.startNode = startNode[0]
		if isinstance(startNode, Point):
			startpoint = startNode
			self.startNode = Node(startpoint)
			self.nodes = [self.startNode]
		self.endNode = None
		self.cost = self.nodes[-1].g_cost
		self.goal = None
	
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
	
	def __len__(self) -> int:
		return len(self.nodes)

class Branch(Path): # Mechanical, Electrical, Plumbing branch
	def __init__(self, startNode: Node, isIndexRoute: bool = False):
		super().__init__(startNode)
		self.sub_branches = []
		self.isIndexRoute = isIndexRoute

class Branch2D(Branch):
	def __init__(self, floorPlan: FloorPlan, startPoint: Union[Node, Point], isIndexRoute: bool = False, ax: plt.Axes=None, visualize = False):
		super().__init__(startPoint, isIndexRoute)
		self.ax = ax # Figure axes
		self.visualize = visualize
		self._visualizer = None
		if isinstance(floorPlan, FloorPlan):
			self.floorPlan = floorPlan
		else:
			raise ValueError("floorPlan must be of type FloorPlan.")

	def generate(self):
		self.pathfinder = Pathfinder(self.floorPlan)
		if self.visualize == True:
			# Initialize the PathfindingVisualizer
			self._visualizer = PathfindingVisualizer(self.pathfinder, self.ax)
		furthest_room = self.pathfinder.findFurthestRoom(self.floorPlan.ahu.position)
		print(f"AHU position: {self.floorPlan.ahu.position}")
		print(f"Furthest room center: {furthest_room.center}")
		# Create route to the furthest room using optimized A* pathfinding
		self.pathfinder.a_star(self.floorPlan.ahu.position, furthest_room.center, self._visualizer)
		self.nodes = self.pathfinder.path