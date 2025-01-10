import pytest
from geometry import Point
from structural import FloorPlan, Room

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