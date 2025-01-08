from core import Node
from geometry import Point


class AirHandlingUnit:
	def __init__(self, position: Point):
		self.position = position
	

class Path:
	'''Class for storing Mechanical, Electrical and Plumbing routes. Each bend/fitting is a node.'''
	def __init__(self, startNode: Node):
		self.startNode = startNode
		self.endNode = None
		self.nodes = [startNode]
		self.length = 0
		self.cost = self.nodes[-1].g

	def add_node(self, node: Node):
		self.nodes.append(node)
		self.startNode = node

class Branch(Path): # Mechanical, Electrical, Plumbing branch
	def __init__(self, startNode: Node, isIndexRoute: bool = False):
		super().__init__(startNode)
		self.sub_branches = []
		self.isIndexRoute = isIndexRoute

