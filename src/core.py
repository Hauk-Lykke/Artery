from abc import ABC, abstractmethod
from geometry import Point

class Node:
    """A node class for A* pathfinding algorithm.
    
    Represents a point in the search space with associated path costs.
    Used to track paths and determine optimal routes.
    
    Attributes:
        position (Point): Coordinates of the node in the search space
        parent (Node): Reference to the previous node in the path
        g_cost (float): Cost from start node to this node
        h (float): Heuristic estimate from this node to goal
        f (float): Total cost (g_cost + h) used for path evaluation
    """
    def __init__(self, position: Point, parent=None):
        self.position = position
        self.parent = parent
        self.g_cost = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

class Cost(ABC):
	@abstractmethod
	def calculate(self, current: Point, next: Point) -> float:
		pass