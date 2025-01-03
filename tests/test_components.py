import pytest
import numpy as np
from src.components import Wall, Room, FloorPlan, WallType

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

def test_room_center():
    # Test room center calculation
    room = Room([(0, 0), (10, 0), (10, 10), (0, 10)])
    assert np.allclose(room.center, np.array([5, 5]))

def test_floor_plan_room_addition():
    floor_plan = FloorPlan()
    room1 = Room([(0, 0), (5, 0), (5, 5), (0, 5)])
    room2 = Room([(5, 0), (10, 0), (10, 5), (5, 5)])
    
    floor_plan.add_rooms([room1, room2])
    assert len(floor_plan._rooms) == 2
    
    # Test wall types are preserved
    room1.walls[0].wall_type = WallType.OUTER_WALL
    assert floor_plan._rooms[0].walls[0].wall_type == WallType.OUTER_WALL
