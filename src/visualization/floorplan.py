
from matplotlib import pyplot as plt

from structural.core import WallType


class FloorPlanVisualizer:
	def __init__(self, ax: plt.Axes):
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

	def update(self, floorPlan):
		if len(floorPlan.rooms):
			all_corners = []
			[all_corners.extend(room.corners) for room in floorPlan.rooms]
			x_min = min([corner.x for corner in all_corners])
			y_min = min([corner.y for corner in all_corners])
			x_max = max([corner.x for corner in all_corners])
			y_max = max([corner.y for corner in all_corners])

			# self.ax.set_xlim((x_min, x_max))
			# self.ax.set_ylim((y_min, y_max))
		# Plot rooms
		for wall in floorPlan.walls:
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
		if floorPlan.ahu is not None:
			self.ax.plot(floorPlan.ahu.position.x, floorPlan.ahu.position.y, 'rs', markersize=10)
		
		# Plot room centers
		for room in floorPlan.rooms:
			self.ax.plot(room.center.x, room.center.y, 'go', markersize=5)
		