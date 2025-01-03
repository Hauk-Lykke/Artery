import pytest
import numpy as np
import matplotlib.pyplot as plt
from src.components import AHU, Building, FloorPlan, Room, Wall, WallType
from src.pathfinding import EuclideanDistance, CompositeHeuristic
import src.routing as routing

def test_wall_creation():
	# Test wall properties
	wall = Wall((0, 0), (3, 4))
	assert np.allclose(wall.start, np.array([0, 0]))
	assert np.allclose(wall.end, np.array([3, 4]))
	assert np.allclose(wall.vector, np.array([3, 4]))
	assert np.allclose(wall.length, 5.0)  # 3-4-5 triangle
	
	# Test angle calculation
	other_vector = np.array([4, -3])  # perpendicular to wall vector
	angle = wall.get_angle_with(other_vector)
	assert 85 <= angle <= 95  # Should be 90 degrees ± numerical precision

def test_room_walls():
	# Create a simple square room
	room = Room([(0, 0), (10, 0), (10, 10), (0, 10)])
	
	# Verify walls were created
	assert hasattr(room, 'walls')
	assert len(room.walls) == 4
	
	# Verify wall properties
	for wall in room.walls:
		assert isinstance(wall, Wall)
		assert wall.length == 10.0

def test_euclidean_heuristic():
    euclidean = EuclideanDistance()
    
    # Test distance calculation
    start = np.array([-1, 5])
    end = np.array([11, 5])
    
    # Expected distance should be 12 (horizontal distance from -1 to 11)
    expected_distance = 12.0
    
    assert np.allclose(euclidean.calculate(start, end), expected_distance)

def test_create_example_rooms_11():
	floor_plan = FloorPlan()
	# Bottom row offices (left to right)
	office_b1 = Room([(0, 0), (5, 0), (5, 10), (0, 10)])
	office_b1.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	office_b1.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
	
	office_b2 = Room([(5, 0), (10, 0), (10, 10), (5, 10)])
	office_b2.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	
	office_b3 = Room([(10, 0), (15, 0), (15, 10), (10, 10)])
	office_b3.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	
	office_b4 = Room([(15, 0), (20, 0), (20, 10), (15, 10)])
	office_b4.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	
	office_b5 = Room([(20, 0), (25, 0), (25, 10), (20, 10)])
	office_b5.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	
	office_b6 = Room([(25, 0), (30, 0), (30, 10), (25, 10)])
	office_b6.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
	office_b6.walls[1].wall_type = WallType.OUTER_WALL  # Right wall

	# Top row offices (left to right)
	office_t1 = Room([(0, 15), (10, 15), (10, 25), (0, 25)])
	office_t1.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
	office_t1.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
	
	office_t2 = Room([(10, 15), (15, 15), (15, 25), (10, 25)])
	office_t2.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
	
	office_t3 = Room([(15, 15), (20, 15), (20, 25), (15, 25)])
	office_t3.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
	
	office_t4 = Room([(20, 15), (25, 15), (25, 25), (20, 25)])
	office_t4.walls[2].wall_type = WallType.OUTER_WALL  # Top wall

	# Small square room (top right)
	square_room = Room([(25, 20), (30, 20), (30, 25), (25, 25)])
	square_room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
	square_room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall

	corridor = Room([(0,10),(0,15),(25,15),(25,20),(30,20),(30,10),(0,10)])
	corridor.walls[0].wall_type = WallType.OUTER_WALL  # Left wall
	corridor.walls[4].wall_type = WallType.OUTER_WALL  # Right wall

	# Add rooms to floor plan
	rooms_to_add = [
		office_b1, office_b2, office_b3, office_b4, office_b5, office_b6,
		office_t1, office_t2, office_t3, office_t4, square_room, corridor
	]
	floor_plan.add_rooms(rooms_to_add)

	# Verify all rooms were created successfully
	for room in floor_plan._rooms:
		assert isinstance(room, Room)
		assert hasattr(room, 'corners')
		assert hasattr(room, 'center')

	# Verify total number of rooms
	assert len(floor_plan._rooms) == 12
	
	ahu = AHU((2.5, 2.5))  # AHU position adjusted to be within the bottom-left room
	floor_plan.ahu = ahu

	routes, fig, ax = routing.route_ducts(floor_plan)
	# plt.close(fig)  # Clean up the figure after test
