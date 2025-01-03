import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from src.components import AHU, Room, Wall, FloorPlan, WallType
from src.core import Node
from src.pathfinding import (
	Pathfinder, EuclideanDistance, MovementCost, 
	WallProximityCost, CompositeCost, CompositeHeuristic
)
import src.routing as routing
import pytest

@pytest.fixture(autouse=True)
def mpl_test_settings():
	import matplotlib
	matplotlib.use('TkAgg')
	plt.ion()
	yield
	plt.close('all')

def test_four_rooms():
	# Create floor plan
	floor_plan = FloorPlan()
	
	# Create four rooms in a 2x2 grid
	rooms = []
	
	# Bottom-left room
	room = Room([(0, 0), (5, 0), (5, 5), (0, 5)])
	room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
	rooms.append(room)
	
	# Bottom-right room
	room = Room([(5, 0), (10, 0), (10, 5), (5, 5)])
	room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
	rooms.append(room)
	
	# Top-left room
	room = Room([(0, 5), (5, 5), (5, 10), (0, 10)])
	room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
	room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
	rooms.append(room)
	
	# Top-right room
	room = Room([(5, 5), (10, 5), (10, 10), (5, 10)])
	room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
	room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
	rooms.append(room)
	
	floor_plan.add_rooms(rooms)
	floor_plan.ahu = AHU((2.5, 2.5))  # AHU in bottom-left room
	pathfinder = Pathfinder(floor_plan)
	
	# Test path to top-right room
	start = floor_plan.ahu.position
	goal = np.array([7.5, 7.5])  # Center of top-right room
	
	path, costs = pathfinder.a_star(start, goal)
	
	# Verify path exists
	assert len(path) > 0, "No path found"
	assert len(costs) > 0, "No costs returned"
	assert len(path) == len(costs), "Path and costs lengths don't match"
	
	# Verify path starts and ends at correct points
	assert np.allclose(path[0], start, atol=0.5), "Path doesn't start at AHU"
	assert np.allclose(path[-1], goal, atol=0.5), "Path doesn't reach goal"
	
	# Test full routing
	routes, fig, ax = routing.route_ducts(floor_plan)
	assert len(routes) > 0, "No routes created"
	
	# Verify each route starts at AHU and has costs
	for route, costs in routes:
		assert len(route) > 0, "Empty route found"
		assert len(costs) > 0, "Empty costs found"
		assert len(route) == len(costs), "Route and costs lengths don't match"
		assert np.allclose(route[0], floor_plan.ahu.position, atol=0.5), "Route doesn't start at AHU"
	
	# Keep the figure open until manually closed
	plt.show(block=True)
