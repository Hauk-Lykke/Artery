import pytest
import numpy as np
import shapely as sh
from structural.core import WallType, Wall2D, Room
from structural.floor_plan import FloorPlan
from geometry import Point, Vector

def test_point_equality():
	point0 = Point(1,2,3)
	point1 = Point(1,2,3)
	assert point0 == point1

def test_wall_properties(wall):
	print(wall)
	assert np.allclose(wall.start.toNumpy(), np.array([0, 0, 0]))
	assert np.allclose(wall.end.toNumpy(), np.array([3, 4, 0]))
	assert isinstance(wall.vector, Vector)
	assert isinstance(wall._shapely, sh.LineString)
	assert isinstance(wall.start, Point)
	assert isinstance(wall.end, Point)
	assert abs(wall.length - 5.0) < 1e-10  # 3-4-5 triangle

def test_wall_angle(wall):
	vector = Vector(4, -3)  # perpendicular to wall vector
	angle = wall.vector.getAngleWith(vector)
	assert 89 <= angle <= 91  # Should be 90 degrees ± numerical precision

def test_room_walls(room):
	# Create a simple square room
	# Verify walls were created
	assert hasattr(room, 'walls')
	assert len(room.walls) == 4
	
	# Verify wall properties
	for wall in room.walls:
		assert isinstance(wall, Wall2D)
		assert wall.length == 10.0

def test_room_center():
	# Test room center calculation
	room = Room([Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)])
	assert np.allclose(room.center.toNumpy(), np.array([5, 5, 0]))

def test_floor_plan_room_addition():
	floor_plan = FloorPlan()
	room1 = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
	room2 = Room([Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)])
	
	floor_plan.addRooms([room1, room2])
	assert len(floor_plan._rooms) == 2
	
	# Test wall types are preserved
	room1.walls[0].wall_type = WallType.OUTER_WALL
	assert floor_plan._rooms[0].walls[0].wall_type == WallType.OUTER_WALL
	
def test_wall_reversal():
	# Original wall
	original_wall = Wall2D(Point(0, 0), Point(3, 4))
	
	# Create reversed wall
	reversed_wall = Wall2D(original_wall.end, original_wall.start)
	
	# Test wall vectors are opposite
	assert np.allclose(original_wall.vector.toNumpy(), -reversed_wall.vector.toNumpy())
	assert original_wall.length == reversed_wall.length

def test_wall_equality():
	wall0 = Wall2D(Point(0, 0), Point(3, 4))
	wall1 = Wall2D(Point(0, 0), Point(3, 4))
	assert wall0==wall1



def test_floor_plan_walls():
	# Test wall list updates correctly
	floor_plan = FloorPlan()
	room1 = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
	room2 = Room([Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)])
	floor_plan.addRoom(room1)
	assert len(floor_plan.walls) == 4
	floor_plan.addRoom(room2)
	assert len(floor_plan._rooms) == 2 
	assert len(floor_plan.walls) == 7  # Shared wall between rooms should be counted once
	
	# Verify walls list contains actual Wall objects
	for wall in floor_plan.walls:
		assert isinstance(wall, Wall2D)


def test_room_creation(complex_floor_plan_fixture):
	"""Test that all rooms are created with correct attributes."""
	for room in complex_floor_plan_fixture._rooms:
		assert isinstance(room, Room)
		assert hasattr(room, 'corners')
		assert hasattr(room, 'center')
	assert len(complex_floor_plan_fixture._rooms) == 12

def testSoundRating(simple_floor_plan_fixture):
	assert(simple_floor_plan_fixture._rooms[0].soundRating==37)

def test_exteriorWalls_basic():
	room0 = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
	floorPlan = FloorPlan([room0])
	outsideWalls = floorPlan.getExteriorWalls()
	assert(len(outsideWalls) == 4)
	assert(isinstance(list(outsideWalls)[0], Wall2D))

def test_exteriorWalls_fixture(simple_floor_plan_fixture):
	floorPlan = simple_floor_plan_fixture
	outsideWalls = floorPlan.getExteriorWalls()
	assert(len(outsideWalls) == 8)
	assert(isinstance(list(outsideWalls)[0], Wall2D))


def test_floorPlan_generate():
	floorPlan = FloorPlan()
	floorPlan.generate()
	assert(len(floorPlan._rooms) >= 3)
	assert(len(floorPlan._rooms) <= 8)

def test_simple_floorPlan_fixture(simple_floor_plan_fixture):
	floorPlan = simple_floor_plan_fixture
	assert(len(floorPlan._rooms) == 4)
	assert(len(floorPlan.walls) == 12)

def test_interiorWalls(simple_floor_plan_fixture):
	floorPlan = simple_floor_plan_fixture
	interiorWalls = floorPlan.getInteriorWalls()
	assert(isinstance(list(interiorWalls)[0], Wall2D))
	assert(len(interiorWalls) == 4)
	