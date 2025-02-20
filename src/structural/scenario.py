from core import Node
from routing import Network2D
from structural.floor_plan import FloorPlan
import random

'''These classes facilitate optimization based on the different load scenarios.'''

class Scenario:
	def __init__(self,floorPlan: FloorPlan):
		if isinstance(floorPlan, FloorPlan):
			self.floorPlan = floorPlan
		else:
			raise ValueError("floorPlan must be of type FloorPlan.")


class Scenario2D(Scenario):
	def __init__(self,floorPlan: FloorPlan=None, network: Network2D=None, generateScenario: bool=False):
		if floorPlan:
			super().__init__(floorPlan)
		elif generateScenario:
			floorPlan = FloorPlan()
			floorPlan.generate()
			self.floorPlan = floorPlan
		if network:
			self.network = network
		elif generateScenario:
			startPoint = random.choice([room.center for room in floorPlan.rooms])
			self.network = Network2D(self.floorPlan, startPoint)

	def evaluate(self):
		self.network.generate()
		self.mepCost = max([node.g_cost for node in self.network.nodes])
		# self.structuralCost = self.wallCost + self.columnCost

class ScenarioOptimization:
	def __init__(self, scenarios: list[Scenario2D]=None):
		if scenarios is not None:
			self.scenarios = scenarios
		else:
			self.scenarios = []

	def optimize(self) -> Scenario2D:
		[scenario.evaluate() for scenario in self.scenarios]
		costs = [scenario.mepCost for scenario in self.scenarios]
		index = costs.index(max(costs))
		return self.scenarios[index]
	
	def randomize(self, numberOfCases: int=0):
		'''Generate a random set of building layouts with generated networks.'''
		if numberOfCases:
			self.numberOfCases = numberOfCases
		if len(self.scenarios):
			for scenario in self.scenarios:
				scenario.evaluate()
				scenario.show()
		else:
			for _ in range(numberOfCases):
				self.scenarios.append(Scenario2D(None, None, generateScenario=True))



