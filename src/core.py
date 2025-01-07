from abc import ABC, abstractmethod
import numpy as np

class Node:
	def __init__(self, position: np.ndarray, parent=None):
		self.position = position
		self.parent = parent
		self.g = 0
		self.h = 0
		self.f = 0

	def __lt__(self, other):
		return self.f < other.f

class Cost(ABC):
	@abstractmethod
	def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
		pass
