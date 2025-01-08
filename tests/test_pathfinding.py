from core import Point
import pytest
import numpy as np
import matplotlib.pyplot as plt
from structural import Wall, FloorPlan, Room
from pathfinding import (
	Pathfinder, EnhancedDistance, MovementCost, 
	CompositeCost, CompositeHeuristic
)
from structural import StandardWallCost
from visualization import PathfindingVisualizer

@pytest.fixture(autouse=True)
def mpl_test_settings():
	plt.ion()  # Interactive mode

def test_enhanced_distance():
	floor_plan = FloorPlan()
	enhanced = EnhancedDistance(floor_plan)
	
	# Test static method
	point1 = Point(0, 0)
	point2 = Point(3, 4)
	assert np.allclose(between_points(point1, point2), 5.0)
	
	# Test as heuristic (should include base distance)
	assert enhanced.calculate(point1, point2) >= 5.0

def test_movement_cost():
	cost = MovementCost()
	
	# Test orthogonal movement
	start = Point(0, 0)
	end = Point(1, 0)
	assert np.allclose(cost.calculate(start, end), 1.0)
	
	# Test diagonal movement
	end = Point(1, 1)
	assert np.allclose(cost.calculate(start, end), np.sqrt(2))

def test_wall_crossing_cost():
	wall = Wall(Point(0, 0), Point(10, 0))  # Horizontal wall
	cost = StandardWallCost(wall)
	
	# Test point far from wall
	point1 = Point(5, 5)
	point2 = Point(6, 5)
	assert cost.calculate(point1, point2) == 0  # No penalty
	
	# Test point near wall
	point3 = Point(5, 0.25)  # Close to wall
	assert cost.calculate(point1, point3) > 0  # Should have penalty
	
	# Test crossing wall
	point4 = Point(5, -1)  # Point on other side of wall
	assert cost.calculate(point1, point4) > cost.calculate(point1, point3)  # Crossing should cost more than proximity

def test_composite_cost():
	cost1 = MovementCost()
	wall = Wall(Point(0, 0), Point(10, 0))
	cost2 = StandardWallCost(wall)
	
	composite = CompositeCost([cost1, cost2])
	
	point1 = Point(0, 2)
	point2 = Point(1, 1)
	
	# Composite cost should be sum of individual costs
	expected = cost1.calculate(point1, point2) + cost2.calculate(point1, point2)
	assert np.allclose(composite.calculate(point1, point2), expected)

def test_composite_heuristic():
	floor_plan = FloorPlan()
	h1 = EnhancedDistance(floor_plan)
	h2 = EnhancedDistance(floor_plan)  # Using same type for simplicity
	
	composite = CompositeHeuristic([h1, h2])
	
	start = Point(0, 0)
	goal = Point(3, 4)
	
	# Should be double the euclidean distance since we're using two identical heuristics
	expected = 2 * EnhancedDistance.between_points(start, goal)
	assert np.allclose(composite.calculate(start, goal), expected)

def test_pathfinder_initialization():
	floor_plan = FloorPlan()
	pathfinder = Pathfinder(floor_plan)
	
	assert hasattr(pathfinder, 'movement_cost')
	assert hasattr(pathfinder, 'composite_h')
	assert isinstance(pathfinder.composite_h, CompositeHeuristic)

def test_a_star_simple_path():
	floor_plan = FloorPlan()
	pathfinder = Pathfinder(floor_plan)
	
	start = Point(0, 0)
	goal = Point(2, 2)
	
	path, costs = pathfinder.a_star(start, goal)
	
	assert len(path) > 0, "No path found"
	assert len(costs) == len(path), "Costs and path lengths don't match"
	assert np.allclose(path[0].to_numpy(), start.to_numpy()), "Path doesn't start at start point"
	assert np.allclose(path[-1].to_numpy(), goal.to_numpy()), "Path doesn't reach goal"

def test_visualization_updates():
	floor_plan = FloorPlan()
	pathfinder = Pathfinder(floor_plan)
	
	start = Point(0, 0)
	goal = Point(2, 2)
	
	fig, ax = plt.subplots()
	pathfinder.a_star(start,goal,ax)	
	assert hasattr(ax, '_visualizer'), "Visualizer not created"
	assert isinstance(ax._visualizer, PathfindingVisualizer), "Wrong visualizer type"
	assert ax._visualizer._iterations > 0, "Iterations not tracked"

def test_a_star_stops_at_goal():
	floor_plan = FloorPlan()
	pathfinder = Pathfinder(floor_plan)
	
	start = Point(0, 0)
	goal = Point(1, 1)  # Simple diagonal move
	
	# First run to get number of iterations
	pathfinder.a_star(start, goal)
	iterations1 = len(pathfinder.nodes)
	
	# Add more nodes around goal that could be explored
	floor_plan.add_room(Room([Point(2, 2),Point(1, 1)]))  # Room near goal
	
	# Second run should take same number of iterations
	pathfinder2 = pathfinder
	pathfinder2.a_star(start, goal)
	iterations2 = len(pathfinder2.nodes)
	
	assert iterations1 == iterations2, "Algorithm continued after finding goal"
	assert np.allclose(pathfinder.nodes[-1].to_numpy(), goal.to_numpy()), "Path doesn't reach goal"
	assert np.allclose(pathfinder2.nodes[-1].to_numpy(), goal.to_numpy()), "Path doesn't reach goal"
