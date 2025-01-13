from datetime import datetime
from typing import List, Tuple, Union
from core import Node
import matplotlib.pyplot as plt
from structural import FloorPlan, Room
from pathfinding import Pathfinder
from geometry import Line, Point
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
	
	def insertNode(self, point: Point) -> Node:
		'''Method that adds a node in the path at the given location.'''
		# Find closest node pair to determine insertion point
		node0, node1 = self.findClosestNodePair(point)
		
		# Create new node
		new_node = Node(point)
		new_node.parentNode = node0
		
		# Find index of node0 
		idx = self.nodes.index(node0)
		
		# Insert new node after node0
		self.nodes.insert(idx + 1, new_node)
		
		# Update parent reference of node1 if it exists
		if idx + 2 < len(self.nodes):
			self.nodes[idx + 2].parentNode = new_node

		return new_node

	def findClosestNodePair(self,point: Point) -> Tuple[Point]:
		nodes = self.nodes.copy()
		nodes.sort(key=lambda x: x.position.distanceTo(point))
		return (nodes[-1],nodes[-2])	

	def getNodeAtPosition(self, point: Point):
		for node in self.nodes:
			if node.position == point:
				return node
		raise ValueError("No node at given position.")

class Branch(Path): # Mechanical, Electrical, Plumbing branch
	def __init__(self, startNode: Node):
		super().__init__(startNode)
		self.sub_branches = []

class Branch2D(Branch):
	def __init__(self, floorPlan: FloorPlan, startPoint: Union[Node, Point], targetPoint: Point, ax: plt.Axes=None, startTime: datetime=None):
		super().__init__(startPoint)
		self.ax = ax # Figure axes
		self._visualizer = None
		if isinstance(floorPlan, FloorPlan):
			self.floorPlan = floorPlan
		else:
			raise ValueError("floorPlan must be of type FloorPlan.")
		if targetPoint is None:
			raise ValueError("No target provided")
		if not isinstance(targetPoint, Point):
			raise ValueError("Target must be a Point.")
		self.target = targetPoint
		self._startTime = startTime

	def generate(self):
		self.pathfinder = Pathfinder(self.floorPlan)
		if self.ax is not None:
			# Initialize the PathfindingVisualizer
			self._visualizer = PathfindingVisualizer(self.pathfinder, self.ax, self._startTime)
		print(f"Start position: {self.startNode.position}")
		print(f"Furthest room center: {self.target}")
		# Create route to the furthest room using optimized A* pathfinding
		self.pathfinder.a_star(self.startNode.position, self.target, self._visualizer)
		self.nodes = self.pathfinder.path


class Network:
	def __init__(self, floorPlan: FloorPlan, startPoint: Point, ax: plt.Axes=None):
		if startPoint is None:
			raise ValueError("startPoint must be provided")
		else:
			if isinstance(startPoint, Point):
				self.startPoint = startPoint
			else:
				raise ValueError("Startpoint must be a Point")
		self.floorPlan = floorPlan
		self.ax = ax # Axes handle to a figure. Visualization will only occur if present
		self.nodes = [] # All nodes in all branches
		self.open_room_set = set(self.floorPlan.rooms) # Rooms remaining
		self.closed_room_set = set() # Rooms that have a supply
		self.sourceRoom = self.getSourceRoom()
		self.startPoint = self.sourceRoom.center
		self.closed_room_set.add(self.sourceRoom)

	def generate(self):
		self.startTime = datetime.now()
		destination = self.findMostDistantRoom(self.startPoint).center
		self.mainBranch = Branch2D(self.floorPlan, self.startPoint, destination,self.ax, self.startTime)
		self.branches = [self.mainBranch] # All existing branches in the network
		self.mainBranch.generate()
		self.nodes.extend(self.mainBranch.nodes)
		while self.open_room_set:
			room = self.open_room_set.pop()
			destination = room.center
			# node0,node1 = self.mainBranch.findClosestNodePair(destination)
			# new_node = self.generate_closest_node(destination)
			closestNode = self.getClosestNode(destination)
			sub_branch = Branch2D(self.floorPlan, closestNode, destination,self.ax, self.startTime)
			sub_branch.generate()
			from visualization import save_figure
			# if self.ax is not None:
			# 	save_figure(self.ax,"test_network")
			self.mainBranch.sub_branches.append(sub_branch)
			self.branches.append(sub_branch)
			self.nodes.extend(sub_branch.nodes)

	def getSourceRoom(self) -> Union[Room, None]:
		"""Find and return the room containing the starting node."""
		for room in self.floorPlan.rooms:
			if room.isInsideRoom(self.startPoint):
				self.closed_room_set.add(room)
				self.open_room_set.remove(room)
				return room
		return None  # Handle case where point isn't in any rooml

	def findMostDistantRoom(self, start: Point) -> Room:
		if not isinstance(start, Point):
			raise ValueError("Start must be a Point.")
		if not self.floorPlan.rooms:
			raise ValueError("Floor plan must have rooms before finding most distant room")
		return max(self.floorPlan.rooms, key=lambda room: room.center.distanceTo(start))

					
					
	def getClosestNode(self, point: Point) -> Node:
		"""Find and return the closest Node to the given point.
		
		Args:
			point (Point): Target point to find closest node to
			
		Returns:
			Node: The closest node from the network
			
		Raises:
			ValueError: If no nodes exist in the network
		"""
		if not self.nodes:
			raise ValueError("No nodes available in network")
		return min(self.nodes, key=lambda node: node.position.distanceTo(point))
	
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
		return nodes[0]
	