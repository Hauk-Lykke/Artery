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
	@pytest.mark.usefixtures("simple_floor_plan")
	def test_display_floor_plan(self,simple_floor_plan):
		fig, ax = plt.subplots()
		visualize_layout(simple_floor_plan,ax)
		plt.show(block=True)
		assert fig
		assert ax

	@pytest.mark.usefixtures("simple_floor_plan")
	def test_visualization_updates(self,simple_floor_plan):
		floor_plan = simple_floor_plan
		start = simple_floor_plan._rooms[0].center
		fig, ax = plt.subplots()
		visualize_layout(simple_floor_plan, ax)
		branch = Branch2D(floor_plan,start,ax=ax, visualize=True)
		branch.generate()
		plt.show(block=True)		
		# Save figure if test_name is provided
		branch.pathfinder._visualizer.save_figure("test_visualization_updates")
		assert isinstance(branch._visualizer, PathfindingVisualizer)
		assert isinstance(ax, plt.Axes)
		assert isinstance(fig, plt.Figure)
		