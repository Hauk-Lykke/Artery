import sys
import os

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from components import AHU, Node, Room
import pathfinding as pf
import routing 
import pytest

def test_four_rooms():
	rooms = [
		Room([(0, 0), (0, 5), (5, 5), (5, 0)]),
		Room([(5, 0), (5, 5), (10, 5), (10, 0)]),
		Room([(0, 5), (0, 10), (5, 10), (5, 5)]),
		Room([(5, 5), (5, 10), (10, 10), (10, 5)])
	]
	
	ahu = AHU((2.5, 2.5))  # AHU position adjusted to be within the bottom-left room


	routes = routing.route_ducts(rooms, ahu)
	print(f"Route created: {routes[0]}")
	assert(True)


test_four_rooms()