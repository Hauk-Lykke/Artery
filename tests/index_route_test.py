import sys
import os
import numpy as np
from src.components import AHU, Node, Room, Wall
from src.pathfinding import (
    Pathfinder, ManhattanDistance, MovementCost, 
    WallCrossingCost, CompositeCost
)
import src.routing as routing
import pytest

def test_four_rooms():
    # Create four rooms in a 2x2 grid
    rooms = [
        Room([(0, 0), (0, 5), (5, 5), (5, 0)]),    # bottom-left
        Room([(5, 0), (5, 5), (10, 5), (10, 0)]),  # bottom-right
        Room([(0, 5), (0, 10), (5, 10), (5, 5)]),  # top-left
        Room([(5, 5), (5, 10), (10, 10), (10, 5)]) # top-right
    ]
    
    ahu = AHU((2.5, 2.5))  # AHU in bottom-left room
    
    # Create manhattan distance heuristic
    manhattan = ManhattanDistance()
    
    # Create wall crossing costs for shared walls
    vertical_wall = Wall((5, 0), (5, 10))  # Vertical wall between left and right rooms
    horizontal_wall = Wall((0, 5), (10, 5))  # Horizontal wall between top and bottom rooms
    
    # Create composite cost for g calculation with both walls
    composite_cost = CompositeCost([
        (MovementCost(), 1.0),
        (WallCrossingCost(vertical_wall), 1.0),
        (WallCrossingCost(horizontal_wall), 1.0)
    ])
    
    # Test path to top-right room
    start = ahu.position
    goal = np.array([7.5, 7.5])  # Center of top-right room
    
    path = Pathfinder.a_star(start, goal, rooms, manhattan, composite_cost)
    
    # Verify path exists
    assert len(path) > 0, "No path found"
    
    # Verify path starts and ends at correct points
    assert np.allclose(path[0], start, atol=0.5), "Path doesn't start at AHU"
    assert np.allclose(path[-1], goal, atol=0.5), "Path doesn't reach goal"
    
    # Test full routing
    routes = routing.route_ducts(rooms, ahu)
    assert len(routes) > 0, "No routes created"
    
    # Verify each route starts at AHU
    for route in routes:
        assert len(route) > 0, "Empty route found"
        assert np.allclose(route[0], ahu.position, atol=0.5), "Route doesn't start at AHU"

def test_wall_crossing_behavior():
    # Create two rooms with a shared wall
    rooms = [
        Room([(0, 0), (0, 5), (5, 5), (5, 0)]),    # left room
        Room([(5, 0), (5, 5), (10, 5), (10, 0)])   # right room
    ]
    
    # Create manhattan distance heuristic
    manhattan = ManhattanDistance()
    
    # Create wall crossing cost with higher weight
    shared_wall = Wall((5, 0), (5, 5))  # Vertical wall between rooms
    wall_cost = WallCrossingCost(shared_wall)
    
    # Create composite cost for g calculation with higher weight on wall crossing
    composite_cost = CompositeCost([(MovementCost(), 1.0), (wall_cost, 2.0)])
    
    start = np.array([2.5, 2.5])  # Left room
    goal = np.array([7.5, 2.5])   # Right room
    
    # Path with wall crossing consideration
    path_with_walls = Pathfinder.a_star(start, goal, rooms, manhattan, composite_cost)
    
    # Path with only manhattan distance
    path_manhattan = Pathfinder.a_star(start, goal, rooms, manhattan)
    
    # Wall crossing path should have more points (trying to cross walls optimally)
    assert len(path_with_walls) >= len(path_manhattan), "Wall crossing not affecting path"
