import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from src.components import AHU, Node, Room, Wall
from src.pathfinding import (
    Pathfinder, EuclideanDistance, MovementCost, 
    WallCrossingCost, WallProximityCost, CompositeCost
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
    pathfinder = Pathfinder(rooms)
    
    # Create euclidean distance heuristic
    euclidean = EuclideanDistance()
    
    # Create wall crossing costs for shared walls
    vertical_wall = Wall((5, 0), (5, 10))  # Vertical wall between left and right rooms
    horizontal_wall = Wall((0, 5), (10, 5))  # Horizontal wall between top and bottom rooms
    
    # Create composite cost for g calculation with both walls
    composite_cost = CompositeCost([
        (MovementCost(), 1.0),
        (WallCrossingCost(vertical_wall), 0.5),
        (WallCrossingCost(horizontal_wall), 0.5),
        (WallProximityCost(vertical_wall), 0.4),
        (WallProximityCost(horizontal_wall), 0.4)
    ])
    
    # Test path to top-right room
    start = ahu.position
    goal = np.array([7.5, 7.5])  # Center of top-right room
    
    path = pathfinder.a_star(start, goal, euclidean, composite_cost)
    
    # Verify path exists
    assert len(path) > 0, "No path found"
    
    # Verify path starts and ends at correct points
    assert np.allclose(path[0], start, atol=0.5), "Path doesn't start at AHU"
    assert np.allclose(path[-1], goal, atol=0.5), "Path doesn't reach goal"
    
    # Test full routing
    routes, fig, ax = routing.route_ducts(rooms, ahu)
    # plt.close(fig)  # Clean up the figure after test
    assert len(routes) > 0, "No routes created"
    
    # Verify each route starts at AHU
    for route in routes:
        assert len(route) > 0, "Empty route found"
        assert np.allclose(route[0], ahu.position, atol=0.5), "Route doesn't start at AHU"
