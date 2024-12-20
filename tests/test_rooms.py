import pytest
from src.components import AHU, Room
import routing

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

