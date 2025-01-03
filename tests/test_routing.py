import pytest
import numpy as np
import matplotlib.pyplot as plt
from src.components import Room, AirHandlingUnit, FloorPlan
from src.routing import route_ducts

def test_route_ducts_basic():
    # Create a simple floor plan for testing
    rooms = [
        Room(np.array([[0, 0], [2, 0], [2, 2], [0, 2]]))
    ]
    ahu = AirHandlingUnit(position=np.array([3, 3]))
    floor_plan = FloorPlan(rooms, ahu)
    
    # Test the routing function
    routes, fig, ax = route_ducts(floor_plan)
    
    # Basic assertions
    assert isinstance(routes, list)
    assert len(routes) == 1
    assert len(routes[0]) == 2  # Should contain (index_route, costs)
    
    # Check route structure
    path, costs = routes[0]
    assert isinstance(path, list)
    assert all(isinstance(pos, np.ndarray) for pos in path)
    assert all(pos.shape == (2,) for pos in path)  # Each point should be a 2D coordinate
    assert isinstance(costs, list)
    assert all(isinstance(cost, (int, float)) for cost in costs)
    assert len(costs) > 0  # Should have costs for each step

def test_route_ducts_missing_ahu():
    # Create floor plan without AHU
    rooms = [
        Room(np.array([[0, 0], [2, 0], [2, 2], [0, 2]]))
    ]
    floor_plan = FloorPlan(rooms=rooms)
    
    # Test that routing fails with appropriate error
    with pytest.raises(ValueError, match="AHU must be set in floor plan before routing ducts"):
        route_ducts(floor_plan)

def test_route_ducts_visualization():
    # Create test floor plan
    rooms = [
        Room(np.array([[0, 0], [2, 0], [2, 2], [0, 2]]))
    ]
    ahu = AirHandlingUnit(position=np.array([3, 3]))
    floor_plan = FloorPlan(rooms=rooms, ahu=ahu)
    
    # Test the routing function
    routes, fig, ax = route_ducts(floor_plan)
    
    # Check visualization outputs
    assert fig is not None
    assert ax is not None
    assert len(ax.lines) > 0  # Should have plotted at least one line
    
    # Clean up matplotlib objects
    plt.close(fig)
