import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from typing import List, Tuple
from src.components import AHU, Room, FloorPlan

colormap = plt.cm.viridis

def visualize_layout(floor_plan: FloorPlan, ax):
	# Plot rooms
	for room in floor_plan._rooms:
		corners = np.vstack((room.corners, room.corners[0]))  # Close the polygon
		ax.plot(corners[:, 0], corners[:, 1], 'b-')
	
	# Plot AHU
	ax.plot(floor_plan.ahu.position[0], floor_plan.ahu.position[1], 'rs', markersize=10)
	
	# Plot room centers
	for room in floor_plan._rooms:
		ax.plot(room.center[0], room.center[1], 'go', markersize=5)
	
	ax.set_title("Building Layout and Duct Routing")
	ax.axis('equal')
	ax.grid(True)

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
