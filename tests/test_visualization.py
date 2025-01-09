import pytest
from matplotlib import pyplot as plt
import numpy as np
from MEP import AirHandlingUnit
from core import Node
from geometry import Point
from pathfinding import Pathfinder
from routing import Branch2D
from structural import FloorPlan, Room, WallType
from visualization import PathfindingVisualizer, visualize_layout

@pytest.fixture(autouse=True)
def mpl_test_settings():
	import matplotlib
	matplotlib.use('TkAgg')
	plt.ion()
	yield
	# plt.close('all')

class TestVisualization:
	@pytest.fixture
	def simple_floor_plan(self):
		corners_room1 = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
		corners_room2 = [Point(10, 0), Point(20, 0), Point(20, 10), Point(10, 10)]
		corners_room3 = [Point(0, 10), Point(10, 10), Point(10, 20), Point(0, 20)]
		corners_room4 = [Point(10, 10), Point(20, 10), Point(20, 20), Point(10, 20)]

		room1 = Room(corners_room1)
		room2 = Room(corners_room2)
		room3 = Room(corners_room3)
		room4 = Room(corners_room4)

		return FloorPlan([room1, room2, room3, room4])


	def test_display_floor_plan(self,simple_floor_plan):
		fig, ax = plt.subplots()
		visualize_layout(simple_floor_plan,ax)
		plt.show(block=True)
		assert fig
		assert ax

	def test_visualization_updates(self, simple_floor_plan):
		floor_plan = simple_floor_plan
		start = simple_floor_plan._rooms[0].center
		fig, ax = plt.subplots()
		visualize_layout(simple_floor_plan, ax)
		branch = Branch2D(simple_floor_plan,start,isIndexRoute=True,ax=ax, visualize=True)
		branch.generate()
		assert isinstance(branch._visualizer, PathfindingVisualizer)
		assert isinstance(ax, plt.Axes)
		assert isinstance(fig, plt.Figure)
		