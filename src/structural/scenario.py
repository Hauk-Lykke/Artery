from routing import Network2D
from structural.floor_plan import FloorPlan
import random
import matplotlib.pyplot as plt

'''These classes facilitate optimization based on the different load scenarios.'''

class Scenario:
	def __init__(self,floorPlan: FloorPlan):
		if isinstance(floorPlan, FloorPlan):
			self.floorPlan = floorPlan
		else:
			raise ValueError("floorPlan must be of type FloorPlan.")


class Scenario2D(Scenario):
	ax: plt.Axes
	def __init__(self,floorPlan: FloorPlan=None, network: Network2D=None, generateScenario: bool=False):
		if floorPlan:
			super().__init__(floorPlan)
		if network:
			self.network = network
		elif generateScenario:			
			self.generate()

	def evaluate(self):
		self.network.generate()
		self.mepCost = max([node.g_cost for node in self.network.nodes])
		# self.structuralCost = self.wallCost + self.columnCost

	def show(self,ax):
		if not isinstance(ax, plt.Axes):
			raise ValueError("Axes must be of type plt.Axes")
		self.ax = ax
		self.floorPlan.show(self.ax)
		self.network.show(self.ax)

	def generate(self):
		self.floorPlan = FloorPlan()
		self.floorPlan.generate()
		roomsBySize = self.floorPlan._rooms.copy()
		roomsBySize.sort(key=lambda room: room.area)
		startPoint = roomsBySize[0].center
		self.network = Network2D(self.floorPlan, startPoint)
		self.evaluate()


class ScenarioOptimization:
	ax: list[plt.Axes]
	scenarios: list[Scenario2D]

	def __init__(self, scenarios: list[Scenario2D]=None, ax: list[plt.Axes]=None):
		if scenarios is not None:
			self.scenarios = scenarios
		else:
			self.scenarios = []
		self.ax = ax
		if self.ax is not None and len(ax) != len(scenarios):
			raise Warning("Number of axes is not equal to the number of scenarios")


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



