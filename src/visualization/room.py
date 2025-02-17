
from matplotlib import pyplot as plt

from structural.core import WallType


class RoomVisualizer:
	def __init__(self, ax: plt.Axes, rooms):
		self.ax = ax
		self.rooms = rooms

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

	def update(self, rooms=None):
		if rooms is not None:
			if len(rooms):
				self.rooms = rooms
				all_corners = []
				[all_corners.extend(room.corners) for room in self.rooms]
				x_min = min([corner.x for corner in all_corners])
				y_min = min([corner.y for corner in all_corners])
				x_max = max([corner.x for corner in all_corners])
				y_max = max([corner.y for corner in all_corners])

				# self.ax.set_xlim((x_min, x_max))
				# self.ax.set_ylim((y_min, y_max))
			self.walls = []
			[self.walls.extend(room.walls) for room in self.rooms]
			# Plot rooms
			for wall in self.walls:
					if wall.wallType == WallType.OUTER_WALL:
						color = 'k'  # Black for outer walls
					elif wall.wallType == WallType.CONCRETE:
						color = 'r'  # Red for concrete walls
					else:
						color = 'b'  # Blue for regular walls
					
					self.ax.plot([wall.start.x, wall.end.x], 
							[wall.start.y, wall.end.y], 
							color=color, linewidth=2)
				
		
		# # Plot AHU
		# if self.ahu is not None:
		# 	self.ax.plot(self.ahu.position.x, self.ahu.position.y, 'rs', markersize=10)
		
		# Plot room centers
		for room in self.rooms:
			self.ax.plot(room.center.x, room.center.y, 'go', markersize=5)
		