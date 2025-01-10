import pytest
from matplotlib import pyplot as plt
from routing import Branch2D
from visualization import PathfindingVisualizer, visualize_layout

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
		visualize_layout(simple_floor_plan_fixture,ax)
		plt.show(block=True)
		assert fig
		assert ax

	@pytest.mark.usefixtures("simple_floor_plan_fixture")
	def test_visualization_updates(self,simple_floor_plan_fixture):
		floor_plan = simple_floor_plan_fixture
		start = simple_floor_plan_fixture.rooms[0].center
		fig, ax = plt.subplots()
		visualize_layout(simple_floor_plan_fixture, ax)
		branch = Branch2D(floor_plan,start,ax=ax, visualize=True)
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
		visualize_layout(simple_floor_plan_fixture, ax)
		indexBranch = Branch2D(simple_floor_plan_fixture,start, ax, visualize=True)
		indexBranch.generate()
		closestNode = indexBranch.findClosestNodePair(simple_floor_plan_fixture.rooms[2].center)
		sub_branch = Branch2D(simple_floor_plan_fixture,closestNode, ax, visualize=True)
		sub_branch.generate()
		assert len(sub_branch) >= 2
		plt.show(block=True)