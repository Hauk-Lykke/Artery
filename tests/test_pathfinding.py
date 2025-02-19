from core import Point
import pytest
import numpy as np
import matplotlib.pyplot as plt
from structural.core import Wall2D,Room
from pathfinding import (EnhancedDistance, MovementCost, 
	CompositeCost, CompositeHeuristic, Pathfinder, WallCost, SoundRatingCost
)
from structural.floor_plan import FloorPlan

@pytest.fixture(autouse=True)
def mpl_test_settings():
	plt.ion()  # Interactive mode

def test_enhanced_distance():
	floor_plan = FloorPlan()
	enhanced = EnhancedDistance(floor_plan)
	
	# Test static method
	point1 = Point(0, 0)
	point2 = Point(3, 4)
	assert np.allclose((point2-point1).length, 5.0)
	
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
	wall = Wall2D(Point(0, 0), Point(10, 0))  # Horizontal wall
	costWeights={
			"distance":1,
			"wallProximity":1,
			"perpendicularWallCrossing":3,
			"angledWallCrossing":10,
			"soundRating":1
		}
	cost = WallCost(wall,costWeights)
	
	# Test point far from wall
	point1 = Point(5, 5)
	point2 = Point(6, 5)
	assert cost.calculate(point1, point2) == 0  # No penalty
	
	# Test point near wall
	point3 = Point(5, 0.25)  # Close to wall
	assert cost.calculate(point1, point3) > 0  # Should have penalty
	
	# Test crossing wall
	point4 = Point(5, -1)  # Point on other side of wall
	crossingCost = cost.calculate(point1, point4)
	proximityCost = cost.calculate(point1, point3) 
	assert crossingCost > proximityCost # Crossing should cost more than proximity

def test_composite_cost():
	cost1 = MovementCost()
	wall = Wall2D(Point(0, 0), Point(10, 0))
	costWeights={
		"distance":1,
		"wallProximity":1,
		"perpendicularWallCrossing":3,
		"angledWallCrossing":10,
		"soundRating":1
	}
	cost2 = WallCost(wall,costWeights)
	
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
	expected = 2 * (start-goal).length
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
	
	pathfinder.a_star(start, goal)
	path = pathfinder.path
	
	assert len(pathfinder) > 0, "No path found"
	assert np.allclose(path[0].position.to_numpy(), start.to_numpy()), "Path doesn't start at start point"
	assert np.allclose(path[-1].position.to_numpy(), goal.to_numpy()), "Path doesn't reach goal"


def test_a_star_stops_at_goal():
	floor_plan = FloorPlan()
	pathfinder = Pathfinder(floor_plan)
	
	start = Point(0, 0)
	goal = Point(1, 1)  # Simple diagonal move
	
	# First run to get number of iterations
	pathfinder.a_star(start, goal)
	iterations1 = len(pathfinder.path)
	
	# Add more nodes around goal that could be explored
	floor_plan.addRoom(Room([Point(2, 2),Point(1, 1)]))  # Room near goal
	
	# Second run should take same number of iterations
	pathfinder2 = pathfinder
	pathfinder2.a_star(start, goal)
	iterations2 = len(pathfinder2.path)
	
	assert iterations1 == iterations2, "Algorithm continued after finding goal"
	assert np.allclose(pathfinder.path[-1].position.to_numpy(), goal.to_numpy()), "Path doesn't reach goal"
	assert np.allclose(pathfinder2.path[-1].position.to_numpy(), goal.to_numpy()), "Path doesn't reach goal"
