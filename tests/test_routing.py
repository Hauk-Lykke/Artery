import pytest
from core import Node
from geometry import Point
from structural import Room, FloorPlan
from MEP import AirHandlingUnit
from routing import Branch2D

class TestRouting:	
	@pytest.mark.usefixtures("simple_floor_plan")
	def test_route_ducts_basic(self,simple_floor_plan):
		start = simple_floor_plan._rooms[0].center
		branch = Branch2D(simple_floor_plan,start)	
		branch.generate()
		assert len(branch.nodes) >= 2
		assert len(branch) >= 2

	@pytest.mark.usefixtures("simple_floor_plan")
	def test_route_ducts_distant_rooms(self):
		rooms = [
			Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
			Room([Point(10, 10), Point(12, 10), Point(12, 12), Point(10, 12)])
		]
		ahu = AirHandlingUnit(position=Point(6, 6))
		floor_plan = FloorPlan(rooms, ahu)
		start = ahu.position
		branch = Branch2D(floor_plan,start)
		branch.generate()
		assert len(branch) >= 2

	@pytest.mark.usefixtures("simple_floor_plan")
	def test_multiple_branches(self,simple_floor_plan):
		start = simple_floor_plan._rooms[0].center
		indexBranch = Branch2D(simple_floor_plan,start)
		closestNode = indexBranch.findClosestNode(simple_floor_plan._rooms[2])
		sub_branch = Branch2D(simple_floor_plan,closestNode)
		sub_branch.generate()
		assert len(sub_branch) >= 2


# # def test_route_ducts_complex_layout():
# # 	rooms = [
# # 		Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)]),
# # 		Room([Point(4, 0), Point(6, 0), Point(6, 2), Point(4, 2)]),
# # 		Room([Point(2, 4), Point(4, 4), Point(4, 6), Point(2, 6)]),
# # 		Room([Point(0, 8), Point(2, 8), Point(2, 10), Point(0, 10)])
# # 	]
# # 	ahu = AirHandlingUnit(position=Point(5, 5))
# # 	floor_plan = FloorPlan(rooms, ahu)
	
# # 	routes, fig, ax = route_ducts(floor_plan)
	
# # 	assert len(routes) == 1
# # 	path, costs = routes[0]
# # 	assert len(path) >= 4
# # 	# plt.close(fig)

# # def test_route_ducts_ahu_inside_room():
# # 	room = Room([Point(0, 0), Point(4, 0), Point(4, 4), Point(0, 4)])
# # 	ahu = AirHandlingUnit(position=Point(2, 2))
# # 	floor_plan = FloorPlan([room], ahu)
	
# # 	routes, fig, ax = route_ducts(floor_plan)
	
# # 	assert len(routes) == 1
# # 	path, costs = routes[0]
# # 	assert len(path) >= 1
# # 	# plt.close(fig)

# def test_route_ducts_negative_coordinates():
# 	rooms = [
# 		Room([Point(-2, -2), Point(0, -2), Point(0, 0), Point(-2, 0)]),
# 		Room([Point(1, 1), Point(3, 1), Point(3, 3), Point(1, 3)])
# 	]
# 	ahu = AirHandlingUnit(position=Point(0, 0))
# 	floor_plan = FloorPlan(rooms, ahu)
	
# 	routes, fig, ax = route_ducts(floor_plan)
	
# 	assert len(routes) == 1
# 	path, costs = routes[0]
# 	assert len(path) >= 2
# 	# plt.close(fig)
# 	with pytest.raises(ValueError, match="AHU must be set in floor plan before routing ducts"):
# 		route_ducts(floor_plan)

# def test_route_ducts_visualization():
# 	# Create test floor plan
# 	rooms = [
# 		Room([Point(0, 0), Point(2, 0), Point(2, 2), Point(0, 2)])
# 	]
# 	ahu = AirHandlingUnit(position=Point(3, 3))
# 	floor_plan = FloorPlan(rooms=rooms, ahu=ahu)
	
# 	# Test the routing function
# 	routes, fig, ax = route_ducts(floor_plan)
	
# 	# Check visualization outputs
# 	assert fig is not None
# 	assert ax is not None
# 	assert len(ax.lines) > 0  # Should have plotted at least one line
	
# 	# Clean up matplotlib objects
# 	# plt.close(fig)
