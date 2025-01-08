from core import Node
from geometry import Point


class AirHandlingUnit:
	def __init__(self, position: Point):
		self.position = position
	

class MEPRoute:
	'''Class for storing Mechanical, Electrical and Plumbing routes. Each bend/fitting is a node.'''
	def __init__(self, startNode: Node):
		self.startNode = startNode
		self.endNode = None
		self.nodes = [startNode]
		self.length = 0

	def add_node(self, node: Node):
		self.nodes.append(node)
		self.startNode = node

class MEPBranch(MEPRoute): # Mechanical, Electrical, Plumbing branch
	def __init__(self, startNode: Node, isIndexRoute: bool = False):
		super().__init__(startNode)
		self.sub_branches = []
		self.isIndexRoute = isIndexRoute

	