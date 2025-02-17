import numpy as np
from core import Node
import matplotlib.pyplot as plt
from datetime import datetime
import os
from pathfinding import Pathfinder
from structural.core import WallType
from geometry import Point
from structural.floor_plan import FloorPlan


class PathfindingVisualizer:
	def __init__(self, pathfinder: Pathfinder, ax: plt.Axes, startTime: datetime):
		"""Initialize visualizer with matplotlib axis"""
		self.pathfinder = pathfinder
		self.ax = ax
		self.colormap = plt.cm.viridis
		self._setup_visualization()
		self._start_time = startTime
		self._iterations = 0

	
	def _setup_visualization(self):
		"""Initialize visualization components"""
		# Setup colorbar if not already present
		if not hasattr(self.ax, '_colorbar'):
			self.ax._cost_mapper = plt.cm.ScalarMappable(cmap=self.colormap, 
														norm=plt.Normalize(vmin=0, vmax=1))
			self.ax._colorbar = plt.colorbar(self.ax._cost_mapper, ax=self.ax, 
											label='Path Cost')
		
		# Store initial axis limits
		self.ax._xlim = self.ax.get_xlim()
		self.ax._ylim = self.ax.get_ylim()
		
		# Add grid and styling
		self.ax.grid(True, linestyle='--', alpha=0.7)
		self.ax.set_title('Path Planning Visualization', pad=20)
		
		# Ensure proper layout
		self.ax.figure.tight_layout()
	
	def _update_title(self):
		"""Update the plot title with current iterations and elapsed time"""
		elapsed_timedelta = datetime.now() - self._start_time
		elapsed_time_obj = (datetime.min + elapsed_timedelta).time()
		formatted_time = elapsed_time_obj.strftime('%M:%S')
		self.ax.set_title(f'Automated duct routing, '
				f'Time: {formatted_time}')

	def save_figure(self, test_name: str):
		"""Save the current figure with test name and timestamp"""
		date_str = datetime.now().strftime("%Y%m%d")
		base_filename = f"results_mep/{test_name}_{date_str}"
		
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
		self.current_max_cost = max(neighbor.g_cost for _, neighbor in list(self.pathfinder.open_list.queue) + [(None, current_node)])
		
		# Update normalization for colorbar
		self.ax._cost_mapper.norm.vmax = self.current_max_cost
		
		# Color nodes based on cost
		normalized_cost = (current_node.g_cost / self.current_max_cost 
						 if self.current_max_cost > 0 else 0)
		color = self.colormap(normalized_cost)
		
		# Plot the explored point
		self.ax.plot(neighbor_pos.x, neighbor_pos.y, 'o', 
					color=color, markersize=2)
		
		# Maintain visualization bounds
		self.ax.set_xlim(self.ax._xlim)
		self.ax.set_ylim(self.ax._ylim)
		
		# Update the colorbar
		self.ax._colorbar.update_normal(self.ax._cost_mapper)

	def update_path(self):
		# Plot routes with color grading based on cost
		points = [node.position for node in self.pathfinder.path]
		costs = [node.g_cost for node in self.pathfinder.path]
		global_max_cost = max(costs) if costs else 1  # Avoid division by zero

		# Normalize costs using global maximum
		normalized_costs = np.array(costs) / global_max_cost if global_max_cost > 0 else np.zeros_like(costs)

		# Create line segments colored by cost
		for i in range(len(points) - 1):
			color = self.colormap(normalized_costs[i])  # Use viridis colormap
			self.ax.plot([points[i].x, points[i + 1].x], 
					[points[i].y, points[i + 1].y], 
					c=color, linewidth=2)

		# Update existing colorbar if present, otherwise create new one
		if hasattr(self.ax, '_cost_mapper'):
			self.ax._cost_mapper.norm.vmax = global_max_cost
			self.ax._colorbar.update_normal(self.ax._cost_mapper)
		else:
			self.ax._cost_mapper = plt.cm.ScalarMappable(cmap=self.colormap, norm=plt.Normalize(vmin=0, vmax=global_max_cost))
			self.ax._colorbar = plt.colorbar(self.ax._cost_mapper, ax=self.ax, label='Path Cost')

			
def save_figure(ax, test_name: str):
	"""Save the current figure with test name and timestamp"""
	date_str = datetime.now().strftime("%Y%m%d")
	base_filename = f"results_mep/{test_name}_{date_str}"
	
	counter = 0
	while os.path.exists(f"{base_filename}_{counter}.png"):
		counter += 1
		
	filename = f"{base_filename}_{counter}.png"
	ax.figure.savefig(filename)
	print(f"Saved figure to {filename}")


class FloorPlanVisualizer:
	def _init_(self, floorPlan: FloorPlan, ax: plt.Axes):
		self.floorPlan = floorPlan
		self.ax = ax

	def show(self):
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
		self.ax.legend(handles=legend_elements, loc='lower right')
		
		self.ax.set_title("Building Layout")
		self.ax.axis('equal')
		self.ax.grid(True)
		self.update()

	def update(self):
		# Plot rooms
		for wall in self.floor_plan.walls:
				if wall.wallType == WallType.OUTER_WALL:
					color = 'k'  # Black for outer walls
				elif wall.wallType == WallType.CONCRETE:
					color = 'r'  # Red for concrete walls
				else:
					color = 'b'  # Blue for regular walls
				
				self.ax.plot([wall.start.x, wall.end.x], 
						[wall.start.y, wall.end.y], 
						color=color, linewidth=2)
		
		# Plot AHU
		if self.floor_plan.ahu is not None:
			self.ax.plot(self.floor_plan.ahu.position.x, self.floor_plan.ahu.position.y, 'rs', markersize=10)
		
		# Plot room centers
		for room in self.floor_plan.rooms:
			self.ax.plot(room.center.x, room.center.y, 'go', markersize=5)
		