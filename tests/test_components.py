import pytest
import numpy as np
import shapely as sh
from structural import WallType, Wall, Room, FloorPlan
from geometry import Point, Vector

@pytest.fixture
def wall():
	return Wall(Point(0,0,0), Point(3, 4,0))

def test_wall_properties(wall):
	print(wall)
	assert np.allclose(wall.start.to_numpy(), np.array([0, 0, 0]))
	assert np.allclose(wall.end.to_numpy(), np.array([3, 4, 0]))
	assert isinstance(wall.vector, Vector)
	assert isinstance(wall._shapely, sh.LineString)
	assert isinstance(wall.start, Point)
	assert isinstance(wall.end, Point)
	assert abs(wall.length - 5.0) < 1e-10  # 3-4-5 triangle

def test_wall_angle(wall):
	vector = Vector(4, -3)  # perpendicular to wall vector
	angle = wall.vector.getAngleWith(vector)
	assert 89 <= angle <= 91  # Should be 90 degrees ± numerical precision

def test_room_walls():
	# Create a simple square room
	room = Room([
		Point(0, 0),
		Point(10, 0),
		Point(10, 10),
		Point(0, 10)
	])  # Changed tuples to Points
	
	# Verify walls were created
	assert hasattr(room, 'walls')
	assert len(room.walls) == 4
	
	# Verify wall properties
	for wall in room.walls:
		assert isinstance(wall, Wall)
		assert wall.length == 10.0

def test_room_center():
	# Test room center calculation
	room = Room([Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)])
	assert np.allclose(room.center.to_numpy(), np.array([5, 5, 0]))

def test_floor_plan_room_addition():
	floor_plan = FloorPlan()
	room1 = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
	room2 = Room([Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)])
	
	floor_plan.add_rooms([room1, room2])
	assert len(floor_plan._rooms) == 2
	
	# Test wall types are preserved
	room1.walls[0].wall_type = WallType.OUTER_WALL
	assert floor_plan._rooms[0].walls[0].wall_type == WallType.OUTER_WALL
	
def test_wall_reversal():
		# Original wall
		original_wall = Wall(Point(0, 0), Point(3, 4))
		
		# Create reversed wall
		reversed_wall = Wall(original_wall.end, original_wall.start)
		
		# Test wall vectors are opposite
		assert np.allclose(original_wall.vector.to_numpy(), -reversed_wall.vector.to_numpy())
		assert original_wall.length == reversed_wall.length

def test_floor_plan_walls():
	# Test wall list updates correctly
	floor_plan = FloorPlan()
	room1 = Room([Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5)])
	room2 = Room([Point(5, 0), Point(10, 0), Point(10, 5), Point(5, 5)])
	
	floor_plan.add_room(room1)
	assert len(floor_plan.walls) == 4
	
	floor_plan.add_room(room2)
	assert len(floor_plan._rooms) == 2 
	assert len(floor_plan.walls) == 7  # Shared wall between rooms should be counted once
	
	# Verify walls list contains actual Wall objects
	for wall in floor_plan.walls:
		assert isinstance(wall, Wall)
