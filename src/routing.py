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
		if startNode is None:
			raise ValueError("Starting point must be either a Node, a Point or a list of Nodes.")

		if isinstance(startNode, Node):
			self.startNode = startNode
			self.nodes = [self.startNode]
			if self.startNode.parentBranch is None:
				self.parentBranch = self.startNode.parentBranch
				self.isIndexRoute = True
			else:
				self.isIndexRoute = False
			self.parentNode = startNode
		if isinstance(startNode, list):
			self.nodes = startNode
			if len(startNode) and isinstance(startNode[0]):
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
	def __init__(self, startNode: Node):
		super().__init__(startNode)
		self.sub_branches = []

class Branch2D(Branch):
	def __init__(self, floorPlan: FloorPlan, startPoint: Union[Node, Point], ax: plt.Axes=None, visualize = False):
		super().__init__(startPoint)
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
		furthest_room = self.pathfinder.findFurthestRoom(self.startNode.position)
		print(f"Start position: {self.startNode.position}")
		print(f"Furthest room center: {furthest_room.center}")
		# Create route to the furthest room using optimized A* pathfinding
		self.pathfinder.a_star(self.startNode.position, furthest_room.center, self._visualizer)
		self.nodes = self.pathfinder.path


class Network:
	def __init__(self, floor_plan: FloorPlan, startPoint: Union[Node, Point],ax: plt.Axes=None, visualize = False):
		self.mainBranch = Branch2D(floor_plan, startPoint,ax,visualize)
		self.startPoint = startPoint
		self.floor_plan = floor_plan
		self.ax = ax # Axes handle to a figure
		self.visualize = visualize # Will the process be visualized or not
		self.branches = [self.mainBranch] # All existing branches in the network
		self.nodes = [] # All nodes in all branches
		self.open_room_set = set(self.floor_plan.rooms) # Rooms remaining
		self.closed_room_set = set() # Rooms that have a supply

	def generate(self):
		self.find_source_room()
		self.mainBranch.generate()
		self.nodes.extend(self.mainBranch.nodes)
		while self.open_room_set:
			room = self.open_room_set.pop()
			destination = room.center
			# node0,node1 = self.mainBranch.findClosestNodePair(destination)
			new_node = self.generate_closest_node(destination)
			sub_branch = Branch2D(self.floor_plan, new_node,self.ax,self.visualize)
			sub_branch.generate()
			from visualization import save_figure
			save_figure(self.ax,"test_network")
			self.mainBranch.sub_branches.append(sub_branch)
			self.branches.append(sub_branch)
			self.nodes.extend(sub_branch.nodes)


	def find_source_room(self) -> Union[Room, None]:
		"""Find and return the room containing the starting node."""
		for room in self.floor_plan.rooms:
			if room.is_inside_room(self.startPoint):
				self.closed_room_set.add(room)
				self.open_room_set.remove(room)
				return room
		return None  # Handle case where point isn't in any rooml

					
	def generate_closest_node(self, point: Point) -> Node:
		"""Find closest point on any path segment and create new node there."""
		min_distance = float('inf')
		closest_segment = None
		
		# Check all path segments
		for branch in self.branches:
			for i in range(len(branch.nodes) - 1):
				node1 = branch.nodes[i]
				node2 = branch.nodes[i + 1]
				line = Line(node1.position, node2.position)
				
				# Project point onto line segment
				projected = line.interpolate(point)
				dist = point.distanceTo(projected)
				
				if dist < min_distance:
					min_distance = dist
					closest_segment = (node1, node2, projected)
		
		if closest_segment:
			node1, node2, projected = closest_segment
			# Create and insert new node at projection point
			new_node = Node(projected)
			new_node.parentNode = node1
			
			# Insert into branch nodes list
			branch_idx = next(i for i, branch in enumerate(self.branches) 
							if node1 in branch.nodes)
			branch = self.branches[branch_idx]
			node_idx = branch.nodes.index(node1)
			branch.nodes.insert(node_idx + 1, new_node)
			
			return new_node
			
		# Fallback to closest existing node if no segments found
		nodes = self.nodes.copy()
		nodes.sort(key=lambda x: x.position.distanceTo(point))
		return nodes[-1]
	