# import pytest
# import numpy as np
# import matplotlib.pyplot as plt
# from structural import Room, FloorPlan, WallType
# from MEP import AirHandlingUnit
# import routing as routing
# from core import Point

# @pytest.fixture(autouse=True)
# def mpl_test_settings():
# 	import matplotlib
# 	matplotlib.use('TkAgg')
# 	plt.ion()
# 	yield
# 	plt.close('all')

# class TestFourRooms:
# 	@pytest.fixture
# 	def four_room_floor_plan(self):
# 		"""Create a 2x2 grid of rooms with outer walls and an AHU."""
# 		floor_plan = FloorPlan()
# 		rooms = []
		
# 		# Bottom-left room
# 		room = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
# 		room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
# 		room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
# 		rooms.append(room)
		
# 		# Bottom-right room
# 		room = Room([Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)])
# 		room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
# 		room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
# 		rooms.append(room)
		
# 		# Top-left room
# 		room = Room([Point(0, 5), Point(5, 5), Point(5, 10), Point(0, 10)])
# 		room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
# 		room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
# 		rooms.append(room)
		
# 		# Top-right room
# 		room = Room([Point(5, 5), Point(10, 5), Point(10, 10), Point(5, 10)])
# 		room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
# 		room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
# 		rooms.append(room)
		
# 		floor_plan.add_rooms(rooms)
# 		floor_plan.ahu = AirHandlingUnit(Point(2.5, 2.5))  # AHU in bottom-left room
# 		return floor_plan

# 	def test_create_path_four_rooms(self,four_room_floor_plan):
