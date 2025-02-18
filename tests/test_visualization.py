from datetime import datetime
import pytest
from matplotlib import pyplot as plt
from routing import Branch2D, Network
from visualization.room import RoomVisualizer
from visualization.path import PathfindingVisualizer, save_figure

@pytest.fixture(autouse=True)
def mpl_test_settings():
	import matplotlib
	matplotlib.use('TkAgg')
	plt.ion()
	yield
	# plt.close('all')

class TestVisualization:
	@pytest.mark.usefixtures("simple_floor_plan_fixture")
	def test_display_floor_plan(self,simple_floor_plan_fixture):
		fig, ax = plt.subplots()
		visualizer = RoomVisualizer(simple_floor_plan_fixture.rooms,ax)
		simple_floor_plan_fixture._visualizer = visualizer
		simple_floor_plan_fixture._visualizer.show()
		plt.show(block=True)
		assert fig
		assert ax

	@pytest.mark.usefixtures("room_plan_11_rooms_random_concrete_fixture")
	def test_display_11_room_floor_plan(self, room_plan_11_rooms_random_concrete_fixture):
		fig, ax = plt.subplots()
		visualizer = RoomVisualizer(room_plan_11_rooms_random_concrete_fixture.rooms,ax)
		room_plan_11_rooms_random_concrete_fixture._visualizer = visualizer
		room_plan_11_rooms_random_concrete_fixture._visualizer.show()
		plt.show(block=True)
		assert fig
		assert ax


	@pytest.mark.usefixtures("simple_floor_plan_fixture")
	def test_visualization_updates(self,simple_floor_plan_fixture):
		floor_plan = simple_floor_plan_fixture
		start = floor_plan.rooms[0].center
		fig, ax = plt.subplots()
		visualizer = RoomVisualizer(simple_floor_plan_fixture.rooms, ax)
		floor_plan._visualizer = visualizer
		floor_plan._visualizer.show()
		branch = Branch2D(floor_plan,start,floor_plan.rooms[2].center, ax,datetime.now())
		branch.generate()
		plt.show(block=True)		
		# Save figure if test_name is provided
		branch.pathfinder._visualizer.save_figure("test_visualization_updates")
		assert isinstance(branch._visualizer, PathfindingVisualizer)
		assert isinstance(ax, plt.Axes)
		assert isinstance(fig, plt.Figure)
		
	def test_visualization_multiple_branches(self,simple_floor_plan_fixture):
		start = simple_floor_plan_fixture.rooms[0].center
		fig, ax = plt.subplots()
		visualizer = RoomVisualizer(simple_floor_plan_fixture.rooms, ax)
		simple_floor_plan_fixture._visualizer = visualizer
		simple_floor_plan_fixture._visualizer.show()
		mostDistantRoom = max(simple_floor_plan_fixture.rooms, key=lambda room: room.center.distanceTo(start))
		indexBranch = Branch2D(simple_floor_plan_fixture,start, mostDistantRoom.center, ax, datetime.now())
		indexBranch.generate()
		(closestNode,_) = indexBranch.getClosestNodePair(simple_floor_plan_fixture.rooms[2].center)
		sub_branch = Branch2D(simple_floor_plan_fixture,closestNode, simple_floor_plan_fixture.rooms[3].center,ax, datetime.now())
		sub_branch.generate()
		assert len(sub_branch) >= 2
		plt.show(block=True)

	@pytest.mark.usefixtures("simple_floor_plan_fixture")
	def test_vizualisation_network(self,simple_floor_plan_fixture):
		start = simple_floor_plan_fixture.rooms[0].center
		fig, ax = plt.subplots()
		simple_floor_plan_fixture.ax = ax
		simple_floor_plan_fixture._visualizer = RoomVisualizer(simple_floor_plan_fixture.rooms, ax)
		simple_floor_plan_fixture._visualizer.show()
		network = Network(simple_floor_plan_fixture,start,ax)
		network.generate()
		save_figure(ax,"test_network")
		assert(isinstance(network.mainBranch, Branch2D))
		assert(isinstance(network.branches, list))
		assert isinstance(ax, plt.Axes)
		assert isinstance(fig, plt.Figure)
		plt.show(block=True)
