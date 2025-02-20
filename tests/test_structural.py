from structural.core import Room
import shapely as sh
from structural.floor_plan import FloorPlan


# @pytest.fixture
# def room():
# 	corners = [Point(0,0,0), Point(4,0,0), Point(4,4,0), Point(0,4,0)]
# 	return Room(corners)


def test_room_polygon(room):
	poly = room._shapelyPoly
	assert(isinstance(room, Room))
	assert(isinstance(poly, sh.geometry.Polygon))

def test_room_area(room):
	area = room.area
	assert(isinstance(area,float))
	assert(area==100)

def test_room_aspect_ratio_ok(room):
	aspect_ratio = 4
	assert(room.aspectRatioOk(aspect_ratio))

def test_roomConformsToAspectRatio(room):
	min_aspect_ratio = 1
	max_aspect_ratio = 4
	assert(room.conformsToAspectRatio(min_aspect_ratio, max_aspect_ratio))

def test_subdivide_room(room):
	(room0,room1) = room.subdivide(direction='vertical')
	assert(isinstance(room0, Room))
	assert(isinstance(room1, Room))
	assert(room0.area + room1.area == room.area)

	(room2, room3) = room.subdivide(direction='horizontal')
	assert(isinstance(room2, Room))
	assert(isinstance(room3, Room))
	assert(room2.area + room3.area == room.area)

def test_generate_floorPlan():
	floorPlan = FloorPlan()
	floorPlan.generate()
	assert(floorPlan.area() == 25*25)
	assert(len(floorPlan.rooms)<=8)
	assert(len(floorPlan.rooms)>=3)