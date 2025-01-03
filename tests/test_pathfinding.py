import pytest
import numpy as np
from src.components import Wall, FloorPlan
from src.pathfinding import (
    Pathfinder, EuclideanDistance, MovementCost, 
    CompositeCost, CompositeHeuristic
)
from src.structural import StandardWallCost

def test_euclidean_distance():
    euclidean = EuclideanDistance()
    
    # Test static method
    point1 = np.array([0, 0])
    point2 = np.array([3, 4])
    assert np.allclose(EuclideanDistance.between_points(point1, point2), 5.0)
    
    # Test as heuristic
    assert np.allclose(euclidean.calculate(point1, point2), 5.0)

def test_movement_cost():
    cost = MovementCost()
    
    # Test orthogonal movement
    start = np.array([0, 0])
    end = np.array([1, 0])
    assert np.allclose(cost.calculate(start, end), 1.0)
    
    # Test diagonal movement
    end = np.array([1, 1])
    assert np.allclose(cost.calculate(start, end), np.sqrt(2))

def test_wall_crossing_cost():
    wall = Wall((0, 0), (10, 0))  # Horizontal wall
    cost = StandardWallCost(wall)
    
    # Test point far from wall
    point1 = np.array([5, 5])
    point2 = np.array([6, 5])
    assert cost.calculate(point1, point2) == 0  # No penalty
    
    # Test point near wall
    point3 = np.array([5, 0.25])  # Close to wall
    assert cost.calculate(point1, point3) > 0  # Should have penalty
    
    # Test crossing wall
    point4 = np.array([5, -1])  # Point on other side of wall
    assert cost.calculate(point1, point4) > cost.calculate(point1, point3)  # Crossing should cost more than proximity

def test_composite_cost():
    cost1 = MovementCost()
    wall = Wall((0, 0), (10, 0))
    cost2 = StandardWallCost(wall)
    
    composite = CompositeCost([cost1, cost2])
    
    point1 = np.array([0, 2])
    point2 = np.array([1, 1])
    
    # Composite cost should be sum of individual costs
    expected = cost1.calculate(point1, point2) + cost2.calculate(point1, point2)
    assert np.allclose(composite.calculate(point1, point2), expected)

def test_composite_heuristic():
    h1 = EuclideanDistance()
    h2 = EuclideanDistance()  # Using same type for simplicity
    
    composite = CompositeHeuristic([h1, h2])
    
    start = np.array([0, 0])
    goal = np.array([3, 4])
    
    # Should be double the euclidean distance since we're using two identical heuristics
    expected = 2 * EuclideanDistance.between_points(start, goal)
    assert np.allclose(composite.calculate(start, goal), expected)

def test_pathfinder_initialization():
    floor_plan = FloorPlan()
    pathfinder = Pathfinder(floor_plan)
    
    assert hasattr(pathfinder, 'composite_cost')
    assert hasattr(pathfinder, 'composite_h')
    assert isinstance(pathfinder.composite_h, CompositeHeuristic)

def test_a_star_simple_path():
    floor_plan = FloorPlan()
    pathfinder = Pathfinder(floor_plan)
    
    start = np.array([0, 0])
    goal = np.array([2, 2])
    
    path, costs = pathfinder.a_star(start, goal)
    
    assert len(path) > 0, "No path found"
    assert len(costs) == len(path), "Costs and path lengths don't match"
    assert np.allclose(path[0], start), "Path doesn't start at start point"
    assert np.allclose(path[-1], goal), "Path doesn't reach goal"
