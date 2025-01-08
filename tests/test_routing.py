from core import Node
import pytest
import numpy as np
import matplotlib.pyplot as plt
from geometry import Point
from structural import Room, FloorPlan
from MEP import AirHandlingUnit
from routing import Branch2D
from visualization import visualize_branch, visualize_layout

def test_route_ducts_basic():
	rooms = [
		Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
		Room([Point(3, 0), Point(5, 0), Point(5, 2), Point(3, 2)]),
	]
	ahu = AirHandlingUnit(position=Point(3, 3))
	floor_plan = FloorPlan(rooms, ahu)
	
	# routes, fig, ax = route_ducts(floor_plan)
	start = Node(ahu.position)
	branch = Branch2D(floor_plan,start,True)	
	branch.generate()
	visualize_branch(branch,)
	assert len(branch) >= 2

	# plt.close(fig)

def test_route_ducts_distant_rooms():
	rooms = [
		Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
		Room([Point(10, 10), Point(12, 10), Point(12, 12), Point(10, 12)])
	]
	ahu = AirHandlingUnit(position=Point(6, 6))
	floor_plan = FloorPlan(rooms, ahu)
	
	routes, fig, ax = route_ducts(floor_plan)
	
	assert len(routes) == 1
	path, costs = routes[0]
	assert len(path) >= 2
	# plt.close(fig)

def test_route_ducts_complex_layout():
	rooms = [
		Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
		Room([Point(4, 0), Point(6, 0), Point(6, 2), Point(4, 2)]),
		Room([Point(2, 4), Point(4, 4), Point(4, 6), Point(2, 6)]),
		Room([Point(0, 8), Point(2, 8), Point(2, 10), Point(0, 10)])
	]
	ahu = AirHandlingUnit(position=Point(5, 5))
	floor_plan = FloorPlan(rooms, ahu)
	
	routes, fig, ax = route_ducts(floor_plan)
	
	assert len(routes) == 1
	path, costs = routes[0]
	assert len(path) >= 4
	# plt.close(fig)

def test_route_ducts_ahu_inside_room():
	room = Room([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
	ahu = AirHandlingUnit(position=Point(2, 2))
	floor_plan = FloorPlan([room], ahu)
	
	routes, fig, ax = route_ducts(floor_plan)
	
	assert len(routes) == 1
	path, costs = routes[0]
	assert len(path) >= 1
	# plt.close(fig)

# def test_route_ducts_negative_coordinates():
# 	rooms = [
# 		Room([Point(-2, -2), Point(0, -2), Point(0, 0), Point(-2, 0)]),
# 		Room([Point(1, 1), Point(3, 1), Point(3, 3), Point(1, 3)])
# 	]
# 	ahu = AirHandlingUnit(position=Point(0, 0))
# 	floor_plan = FloorPlan(rooms, ahu)
	
# 	routes, fig, ax = route_ducts(floor_plan)
	
# 	assert len(routes) == 1
# 	path, costs = routes[0]
# 	assert len(path) >= 2
# 	# plt.close(fig)
# 	with pytest.raises(ValueError, match="AHU must be set in floor plan before routing ducts"):
# 		route_ducts(floor_plan)

def test_route_ducts_visualization():
	# Create test floor plan
	rooms = [
		Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)])
	]
	ahu = AirHandlingUnit(position=Point(3, 3))
	floor_plan = FloorPlan(rooms=rooms, ahu=ahu)
	
	# Test the routing function
	routes, fig, ax = route_ducts(floor_plan)
	
	# Check visualization outputs
	assert fig is not None
	assert ax is not None
	assert len(ax.lines) > 0  # Should have plotted at least one line
	
	# Clean up matplotlib objects
	# plt.close(fig)
