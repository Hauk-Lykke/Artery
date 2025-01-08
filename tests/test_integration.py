import pytest
import numpy as np
import matplotlib.pyplot as plt
from structural import Room, FloorPlan, WallType
from MEP import AirHandlingUnit
import routing as routing
from core import Point

@pytest.fixture(autouse=True)
def mpl_test_settings():
	import matplotlib
	matplotlib.use('TkAgg')
	plt.ion()
	yield
	plt.close('all')

class TestFourRooms:
	@pytest.fixture
	def four_room_floor_plan(self):
		"""Create a 2x2 grid of rooms with outer walls and an AHU."""
		floor_plan = FloorPlan()
		rooms = []
		
		# Bottom-left room
		room = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
		room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
		rooms.append(room)
		
		# Bottom-right room
		room = Room([Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)])
		room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
		rooms.append(room)
		
		# Top-left room
		room = Room([Point(0, 5), Point(5, 5), Point(5, 10), Point(0, 10)])
		room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
		room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
		rooms.append(room)
		
		# Top-right room
		room = Room([Point(5, 5), Point(10, 5), Point(10, 10), Point(5, 10)])
		room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
		room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
		rooms.append(room)
		
		floor_plan.add_rooms(rooms)
		floor_plan.ahu = AirHandlingUnit(Point(2.5, 2.5))  # AHU in bottom-left room
		return floor_plan

	def test_duct_routing(self, four_room_floor_plan):
		"""Test that valid duct routes can be created from the AHU to each room."""
		routes, fig, ax = routing.route_ducts(four_room_floor_plan, "test_four_rooms")
		
		# Verify routes
		for route, costs in routes:
			assert len(route) > 0, "Empty route found"
			assert len(costs) > 0, "Empty costs found"
			assert len(route) == len(costs), "Route and costs lengths don't match"
			assert np.allclose(route[0].to_numpy(), four_room_floor_plan.ahu.position.to_numpy(), atol=0.5), "Route doesn't start at AHU"

class TestComplexLayout:
	@pytest.fixture
	def complex_floor_plan(self):
		"""Create a complex 11-room layout with a corridor."""
		floor_plan = FloorPlan()
		
		# Bottom row offices (left to right)
		office_b1 = Room([Point(0, 0), Point(5, 0), Point(5, 10), Point(0, 10)])
		office_b1.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		office_b1.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
		
		office_b2 = Room([Point(5, 0), Point(10, 0), Point(10, 10), Point(5, 10)])
		office_b2.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		
		office_b3 = Room([Point(10, 0), Point(15, 0), Point(15, 10), Point(10, 10)])
		office_b3.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		
		office_b4 = Room([Point(15, 0), Point(20, 0), Point(20, 10), Point(15, 10)])
		office_b4.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		
		office_b5 = Room([Point(20, 0), Point(25, 0), Point(25, 10), Point(20, 10)])
		office_b5.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		
		office_b6 = Room([Point(25, 0), Point(30, 0), Point(30, 10), Point(25, 10)])
		office_b6.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
		office_b6.walls[1].wall_type = WallType.OUTER_WALL  # Right wall

		# Top row offices (left to right)
		office_t1 = Room([Point(0, 15), Point(10, 15), Point(10, 25), Point(0, 25)])
		office_t1.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
		office_t1.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
		
		office_t2 = Room([Point(10, 15), Point(15, 15), Point(15, 25), Point(10, 25)])
		office_t2.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
		
		office_t3 = Room([Point(15, 15), Point(20, 15), Point(20, 25), Point(15, 25)])
		office_t3.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
		
		office_t4 = Room([Point(20, 15), Point(25, 15), Point(25, 25), Point(20, 25)])
		office_t4.walls[2].wall_type = WallType.OUTER_WALL  # Top wall

		# Small square room (top right)
		square_room = Room([Point(25, 20), Point(30, 20), Point(30, 25), Point(25, 25)])
		square_room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
		square_room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall

		corridor = Room([Point(0,10),Point(0,15),Point(25,15),Point(25,20),Point(30,20),Point(30,10),Point(0,10)])
		corridor.walls[0].wall_type = WallType.OUTER_WALL  # Left wall
		corridor.walls[4].wall_type = WallType.OUTER_WALL  # Right wall

		# Add rooms to floor plan
		rooms_to_add = [
			office_b1, office_b2, office_b3, office_b4, office_b5, office_b6,
			office_t1, office_t2, office_t3, office_t4, square_room, corridor
		]
		floor_plan.add_rooms(rooms_to_add)
		floor_plan.ahu = AirHandlingUnit(Point(2.5, 2.5))  # AHU in bottom-left room
		return floor_plan

	def test_room_creation(self, complex_floor_plan):
		"""Test that all rooms are created with correct attributes."""
		for room in complex_floor_plan._rooms:
			assert isinstance(room, Room)
			assert hasattr(room, 'corners')
			assert hasattr(room, 'center')
		assert len(complex_floor_plan._rooms) == 12

	def test_duct_routing(self, complex_floor_plan):
		"""Test that valid duct routes can be created from the AHU to each room."""
		routes, fig, ax = routing.route_ducts(complex_floor_plan, "test_complex_rooms")
		
		assert len(routes) > 0, "No routes created"
		for route, costs in routes:
			assert len(route) > 0, "Empty route found"
			assert len(costs) > 0, "Empty costs found"
			assert len(route) == len(costs), "Route and costs lengths don't match"
			assert np.allclose(route[0].to_numpy(), complex_floor_plan.ahu.position.to_numpy(), atol=0.5), "Route doesn't start at AHU"
