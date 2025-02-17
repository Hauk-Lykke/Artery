import pytest
from geometry import Point
from structural.core import Room
import shapely as sh
from tests.conftest import room


# @pytest.fixture
# def room():
# 	corners = [Point(0,0,0), Point(4,0,0), Point(4,4,0), Point(0,4,0)]
# 	return Room(corners)


def test_room_polygon(room):
	poly = room._shapelyPoly
	assert(isinstance(room, Room))
	assert(isinstance(poly, sh.geometry.Polygon))