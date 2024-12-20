import pytest
import numpy as np
from src.components import AHU, Room, Wall
from src.pathfinding import WallCrossingHeuristic, ManhattanDistance, CompositeHeuristic
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

def test_wall_crossing_heuristic():
    # Create a simple room
    room = Room([(0, 0), (10, 0), (10, 10), (0, 10)])
    # We'll test with the left wall of the room (from (0,0) to (0,10))
    heuristic = WallCrossingHeuristic(room.walls[3])  # Left wall
    
    # Test perpendicular crossing
    cost = heuristic.calculate(np.array([-1, 5]), np.array([11, 5]))
    assert cost == heuristic.perpendicular_cost  # Should cross one wall perpendicularly
    
    # Test angled crossing
    cost = heuristic.calculate(np.array([-1, -1]), np.array([11, 11]))
    assert cost == heuristic.angled_cost  # Should cross one wall at ~45 degrees

def test_composite_heuristic():
    room = Room([(0, 0), (10, 0), (10, 10), (0, 10)])
    manhattan = ManhattanDistance()
    wall_crossing = WallCrossingHeuristic(room.walls[3])  # Left wall
    
    composite = CompositeHeuristic([
        (manhattan, 1.0),
        (wall_crossing, 1.0)
    ])
    
    # Test combined cost
    start = np.array([-1, 5])
    end = np.array([11, 5])
    
    expected_cost = (
        manhattan.calculate(start, end) +  # Manhattan distance
        wall_crossing.calculate(start, end)  # Wall crossing cost
    )
    
    assert np.allclose(composite.calculate(start, end), expected_cost)

def test_create_example_rooms_11():
    # Bottom row offices (left to right)
    office_b1 = Room([(0, 0), (5, 0), (5, 10), (0, 10)])
    office_b2 = Room([(5, 0), (10, 0), (10, 10), (5, 10)])
    office_b3 = Room([(10, 0), (15, 0), (15, 10), (10, 10)])
    office_b4 = Room([(15, 0), (20, 0), (20, 10), (15, 10)])
    office_b5 = Room([(20, 0), (25, 0), (25, 10), (20, 10)])
    office_b6 = Room([(25, 0), (30, 0), (30, 10), (25, 10)])

    # Top row offices (left to right)
    office_t1 = Room([(0, 15), (10, 15), (10, 25), (0, 25)])
    office_t2 = Room([(10, 15), (15, 15), (15, 25), (10, 25)])
    office_t3 = Room([(15, 15), (20, 15), (20, 25), (15, 25)])
    office_t4 = Room([(20, 15), (25, 15), (25, 25), (20, 25)])

    # Small square room (top right)
    square_room = Room([(25, 20), (30, 20), (30, 25), (25, 25)])

    # List of all rooms
    rooms = [
        office_b1, office_b2, office_b3, office_b4, office_b5, office_b6,
        office_t1, office_t2, office_t3, office_t4, square_room
    ]

    # Verify all rooms were created successfully
    for room in rooms:
        assert isinstance(room, Room)
        assert hasattr(room, 'corners')
        assert hasattr(room, 'center')

    # Verify total number of rooms
    assert len(rooms) == 11
    
    ahu = AHU((2.5, 2.5))  # AHU position adjusted to be within the bottom-left room


    routes = routing.route_ducts(rooms, ahu)
