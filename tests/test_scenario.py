import pytest
from routing import Network2D
from structural.floor_plan import FloorPlan
from structural.scenario import Scenario2D, ScenarioOptimization

@pytest.mark.usefixtures("simple_floor_plan_fixture")
def test_scenario_create(simple_floor_plan_fixture):
	network = Network2D(simple_floor_plan_fixture,simple_floor_plan_fixture.rooms[0].center)
	scenario = Scenario2D(simple_floor_plan_fixture, network)
	assert(isinstance(scenario, Scenario2D))
	assert(isinstance(scenario.network, Network2D))

@pytest.mark.usefixtures("simple_floor_plan_fixture")
def test_scenarioOptimization_optimize(simple_floor_plan_fixture):
	network = Network2D(simple_floor_plan_fixture,simple_floor_plan_fixture.rooms[0].center)
	network.generate()
	scenario = Scenario2D(simple_floor_plan_fixture, network)
	scenario.evaluate()
	scenarioOptimization = ScenarioOptimization([scenario])
	result = scenarioOptimization.optimize()
	assert(isinstance(result, Scenario2D))

# @pytest.mark.usefixtures("complex_floor_plan_fixture")
# def test_scenarioOptimization_randomize(complex_floor_plan_fixture):

def test_scenarioOptimization_randomize():
	scenarioOptimization = ScenarioOptimization()
	scenarioOptimization.randomize(2)
	# optimalScenario = scenarioOptimization.optimize()
	assert(len(scenarioOptimization.scenarios) == 2)