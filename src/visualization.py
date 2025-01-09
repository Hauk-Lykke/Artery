from core import Node
import matplotlib.pyplot as plt
import datetime
import os
from pathfinding import Pathfinder
from structural import FloorPlan, WallType
from geometry import Point


def visualize_layout(floor_plan: FloorPlan, ax):
	# Plot rooms
	for room in floor_plan._rooms:
		# Plot each wall with appropriate color based on type
		for wall in room.walls:
			if wall.wall_type == WallType.OUTER_WALL:
				color = 'k'  # Black for outer walls
			elif wall.wall_type == WallType.CONCRETE:
				color = 'r'  # Red for concrete walls
			else:
				color = 'b'  # Blue for regular walls
			
			ax.plot([wall.start.x, wall.end.x], 
					[wall.start.y, wall.end.y], 
					color=color, linewidth=2)
	
	# Plot AHU
	ax.plot(floor_plan.ahu.position.x, floor_plan.ahu.position.y, 'rs', markersize=10)
	
	# Plot room centers
	for room in floor_plan._rooms:
		ax.plot(room.center.x, room.center.y, 'go', markersize=5)
	
	# Add wall type legend
	from matplotlib.lines import Line2D
	legend_elements = [
		Line2D([0], [0], color='k', label='Outer Wall', linewidth=2),
		Line2D([0], [0], color='r', label='Concrete Wall', linewidth=2),
		Line2D([0], [0], color='b', label='Regular Wall', linewidth=2),
		Line2D([0], [0], color='none', marker='s', markerfacecolor='r', 
			   label='AHU', markersize=10),
		Line2D([0], [0], color='none', marker='o', markerfacecolor='g', 
			   label='Room Center', markersize=5)
	]
	ax.legend(handles=legend_elements, loc='lower right')
	
	ax.set_title("Building Layout and Duct Routing")
	ax.axis('equal')
	ax.grid(True)

class PathfindingVisualizer:
	def __init__(self, pathfinder: Pathfinder, ax):
		"""Initialize visualizer with matplotlib axis"""
		self.pathfinder = pathfinder
		self.ax = ax
		self._setup_visualization()
		self._start_time = datetime.datetime.now()
		self._iterations = 0
		self.colormap = plt.cm.viridis
	
	def _setup_visualization(self):
		"""Initialize visualization components"""
		self.ax._cost_mapper = plt.cm.ScalarMappable(cmap=self.colormap, 
													norm=plt.Normalize(vmin=0, vmax=1))
		self.ax._colorbar = plt.colorbar(self.ax._cost_mapper, ax=self.ax, 
									   label='Path Cost')
		# Store initial axis limits
		self.ax._xlim = self.ax.get_xlim()
		self.ax._ylim = self.ax.get_ylim()
	
	def _update_title(self):
		"""Update the plot title with current iterations and elapsed time"""
		elapsed = (datetime.datetime.now() - self._start_time).total_seconds()
		self.ax.set_title(f'A* Pathfinding - Iterations: {self._iterations}, '
						 f'Time: {elapsed:.2f}s')

	def save_figure(self, test_name: str):
		"""Save the current figure with test name and timestamp"""
		date_str = datetime.datetime.now().strftime("%Y%m%d")
		base_filename = f"results/{test_name}_{date_str}"
		
		counter = 0
		while os.path.exists(f"{base_filename}_{counter}.png"):
			counter += 1
			
		filename = f"{base_filename}_{counter}.png"
		self.ax.figure.savefig(filename)
		print(f"Saved figure to {filename}")
		
	def update_node(self, current_node: Node, neighbor_pos: Point):
		"""Visualize a single node exploration step"""
		self._iterations += 1
		self._update_title()
		
		# Get max cost from open list and current node
		current_max_cost = max(neighbor.g for _, neighbor in list(self.pathfinder.open_list.queue) 
							 + [(0, current_node)])
		
		# Update normalization for colorbar
		self.ax._cost_mapper.norm.vmax = current_max_cost
		
		# Color nodes based on cost
		normalized_cost = (current_node.g / current_max_cost 
						 if current_max_cost > 0 else 0)
		color = self.colormap(normalized_cost)
		
		# Plot the explored point
		self.ax.plot(neighbor_pos.x, neighbor_pos.y, 'o', 
					color=color, markersize=2)
		
		# Maintain visualization bounds
		self.ax.set_xlim(self.ax._xlim)
		self.ax.set_ylim(self.ax._ylim)
		
		# Update the colorbar
		self.ax._colorbar.update_normal(self.ax._cost_mapper)