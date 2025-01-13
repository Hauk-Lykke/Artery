import pytest
from MEP import AirHandlingUnit
from geometry import Point
from structural import FloorPlan, Room, WallType

@pytest.fixture
def simple_fixture():
	return "teststring"

@pytest.fixture(scope="module")
def simple_floor_plan_fixture():
	corners_room1 = [Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)]
	corners_room2 = [Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)]
	corners_room3 = [Point(0, 5), Point(5, 5), Point(5, 10), Point(0, 10)]
	corners_room4 = [Point(5, 5), Point(10, 5), Point(10, 10), Point(5, 10)]

	room1 = Room(corners_room1)
	room2 = Room(corners_room2)
	room3 = Room(corners_room3)
	room4 = Room(corners_room4)
	return FloorPlan([room1, room2, room3, room4])



@pytest.fixture(scope="module")
def complex_floor_plan_fixture():
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

	corridor = Room([Point(0,10),Point(0,15),Point(25,15),Point(25,20),Point(30,20),Point(30,10)])
	corridor.walls[0].wall_type = WallType.OUTER_WALL  # Left wall
	corridor.walls[4].wall_type = WallType.OUTER_WALL  # Right wall

	# Add rooms to floor plan
	rooms_to_add = [
		office_b1, office_b2, office_b3, office_b4, office_b5, office_b6,
		office_t1, office_t2, office_t3, office_t4, square_room, corridor
	]
	floor_plan.addRooms(rooms_to_add)
	floor_plan.ahu = AirHandlingUnit(Point(2.5, 2.5))  # AHU in bottom-left room
	return floor_plan

