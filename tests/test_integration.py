import pytest
import numpy as np
import matplotlib.pyplot as plt
from src.components import AHU, Room, FloorPlan, WallType
import src.routing as routing

@pytest.fixture(autouse=True)
def mpl_test_settings():
    import matplotlib
    matplotlib.use('TkAgg')
    plt.ion()
    yield
    plt.close('all')

def test_four_rooms():
    """Test the complete system with a simple 2x2 room layout"""
    floor_plan = FloorPlan()
    
    # Create four rooms in a 2x2 grid
    rooms = []
    
    # Bottom-left room
    room = Room([(0, 0), (5, 0), (5, 5), (0, 5)])
    room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
    room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
    rooms.append(room)
    
    # Bottom-right room
    room = Room([(5, 0), (10, 0), (10, 5), (5, 5)])
    room.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
    room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
    rooms.append(room)
    
    # Top-left room
    room = Room([(0, 5), (5, 5), (5, 10), (0, 10)])
    room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
    room.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
    rooms.append(room)
    
    # Top-right room
    room = Room([(5, 5), (10, 5), (10, 10), (5, 10)])
    room.walls[1].wall_type = WallType.OUTER_WALL  # Right wall
    room.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
    rooms.append(room)
    
    floor_plan.add_rooms(rooms)
    floor_plan.ahu = AHU((2.5, 2.5))  # AHU in bottom-left room
    
    # Test full routing
    routes, fig, ax = routing.route_ducts(floor_plan)
    
    # Verify routes
    assert len(routes) > 0, "No routes created"
    for route, costs in routes:
        assert len(route) > 0, "Empty route found"
        assert len(costs) > 0, "Empty costs found"
        assert len(route) == len(costs), "Route and costs lengths don't match"
        assert np.allclose(route[0], floor_plan.ahu.position, atol=0.5), "Route doesn't start at AHU"

def test_complex_layout():
    """Test the system with a more complex 11-room layout"""
    floor_plan = FloorPlan()
    
    # Bottom row offices (left to right)
    office_b1 = Room([(0, 0), (5, 0), (5, 10), (0, 10)])
    office_b1.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
    office_b1.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
    
    office_b2 = Room([(5, 0), (10, 0), (10, 10), (5, 10)])
    office_b2.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
    
    office_b3 = Room([(10, 0), (15, 0), (15, 10), (10, 10)])
    office_b3.walls[0].wall_type = WallType.OUTER_WALL  # Bottom wall
    
    # Top row offices
    office_t1 = Room([(0, 15), (10, 15), (10, 25), (0, 25)])
    office_t1.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
    office_t1.walls[3].wall_type = WallType.OUTER_WALL  # Left wall
    
    office_t2 = Room([(10, 15), (15, 15), (15, 25), (10, 25)])
    office_t2.walls[2].wall_type = WallType.OUTER_WALL  # Top wall
    
    # Corridor
    corridor = Room([(0,10), (0,15), (15,15), (15,10), (0,10)])
    corridor.walls[0].wall_type = WallType.OUTER_WALL  # Left wall
    
    # Add rooms to floor plan
    rooms = [office_b1, office_b2, office_b3, office_t1, office_t2, corridor]
    floor_plan.add_rooms(rooms)
    floor_plan.ahu = AHU((2.5, 2.5))
    
    # Test routing
    routes, fig, ax = routing.route_ducts(floor_plan)
    
    # Verify routes
    assert len(routes) > 0, "No routes created"
    for route, costs in routes:
        assert len(route) > 0, "Empty route found"
        assert len(costs) > 0, "Empty costs found"
        assert len(route) == len(costs), "Route and costs lengths don't match"
        assert np.allclose(route[0], floor_plan.ahu.position, atol=0.5), "Route doesn't start at AHU"
