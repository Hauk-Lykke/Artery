import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Tuple
from src.components import AHU, Room, FloorPlan, WallType

colormap = plt.cm.viridis

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
			
			ax.plot([wall.start[0], wall.end[0]], 
					[wall.start[1], wall.end[1]], 
					color=color, linewidth=2)
	
	# Plot AHU
	ax.plot(floor_plan.ahu.position[0], floor_plan.ahu.position[1], 'rs', markersize=10)
	
	# Plot room centers
	for room in floor_plan._rooms:
		ax.plot(room.center[0], room.center[1], 'go', markersize=5)
	
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
    def __init__(self, ax):
        self.ax = ax
        self._setup_visualization()
    
    def _setup_visualization(self):
        """Initialize visualization components"""
        self.ax._cost_mapper = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=plt.Normalize(vmin=0, vmax=1))
        self.ax._colorbar = plt.colorbar(self.ax._cost_mapper, ax=self.ax, label='Path Cost')
        # Store initial axis limits
        self.ax._xlim = self.ax.get_xlim()
        self.ax._ylim = self.ax.get_ylim()
    
    def update_node(self, current_node, neighbor_pos, open_list):
        """Visualize a single node exploration step"""
        # Update the maximum cost seen so far
        current_max_cost = max(neighbor.g for _, neighbor in list(open_list.queue) + [(0, current_node)])
        
        # Update normalization for colorbar
        self.ax._cost_mapper.norm.vmax = current_max_cost
        
        # Color the attempted nodes based on cost relative to current maximum
        normalized_cost = current_node.g / current_max_cost if current_max_cost > 0 else 0
        color = colormap(normalized_cost)
        self.ax.plot(neighbor_pos[0], neighbor_pos[1], 'o', color=color, markersize=2)
        
        # Restore axis limits
        self.ax.set_xlim(self.ax._xlim)
        self.ax.set_ylim(self.ax._ylim)
        
        # Update colorbar
        self.ax._colorbar.update_normal(self.ax._cost_mapper)

def visualize_routing(routes: List[Tuple[List[np.ndarray], List[float]]], ax):
	# Find global maximum cost for consistent color mapping
	global_max_cost = max(max(costs) for _, costs in routes)
	
	# Plot routes with color grading based on cost
	for route, costs in routes:
		route_array = np.array(route)
		points = route_array[:-1]  # All points except the last
		next_points = route_array[1:]  # All points except the first
		
		# Normalize costs using global maximum
		normalized_costs = np.array(costs[:-1]) / global_max_cost if global_max_cost > 0 else np.zeros_like(costs[:-1])
		
		# Create line segments colored by cost
		for i in range(len(points)):
			color = colormap(normalized_costs[i])  # Use viridis colormap
			ax.plot([points[i][0], next_points[i][0]], 
				   [points[i][1], next_points[i][1]], 
				   c=color, linewidth=2)
	
	# Update existing colorbar if present, otherwise create new one
	if hasattr(ax, '_cost_mapper'):
		ax._cost_mapper.norm.vmax = global_max_cost
		ax._colorbar.update_normal(ax._cost_mapper)
	else:
		ax._cost_mapper = plt.cm.ScalarMappable(cmap=colormap, norm=plt.Normalize(vmin=0, vmax=global_max_cost))
		ax._colorbar = plt.colorbar(ax._cost_mapper, ax=ax, label='Path Cost')
