"""
Generate multiple random floor layouts. Plots the 

Planned changes:
- Export rooms to CSV
- Remove plotting - plot can be made in seperate python file
- Make classes and methods for floors, rooms, columns, beams, ducts.
    We want to be able to
        - Store each floors in a file (csv?)
        - Plot a floor with all elements
"""

import random
import os
import matplotlib.pyplot as plt

from shapely.geometry import Polygon

from MEP import AirHandlingUnit
from structural.core import Room


class FloorPlan:
	def __init__(self, rooms: list[Room] = None, ahu: AirHandlingUnit = None):
		self.walls = set()
		self.ahu = None  # Initialize as None by default
		self.rooms = []
		if rooms is not None:
			self.addRooms(rooms)
		if ahu is not None:
			self.ahu = ahu

	def addRoom(self, room):
		self.rooms.append(room)
		self.updateWalls()

	def updateWalls(self):
		# uniqueWalls = set()
		for room in self.rooms:
			for wall in room.walls:
				reverse_wall = wall.reverse()
				if wall not in self.walls and reverse_wall not in self.walls:
					self.walls.add(wall)
		# self.walls = list(self.walls) # Would be nice if walls were somehow ordered, but that's for later

	def addRooms(self, rooms):
		for room in rooms:
			self.addRoom(room)

class Building:
		def __init__(self, floorPlans: list = [FloorPlan]):
			self.floor_plans = floorPlans



# def area(room): #Integrate into floorplan class
#     """Returns area of a rectangular room (x1, y1, x2, y2)."""
#     (x1, y1, x2, y2) = room
#     return abs(x2 - x1) * abs(y2 - y1)


def room_conforms(room, min_a, max_ratio):
    """Checks if room area and aspect ratio are within limits."""
    a = area(room)
    return (min_a <= a) and aspect_ratio_ok(room, max_ratio)

def subdivide_room(room, direction):
    """
    Splits room randomly in 'vertical' or 'horizontal' direction.
    Returns two new rooms if the split is valid, else None.
    """
    (x1, y1, x2, y2) = room
    w = abs(x2 - x1)
    h = abs(y2 - y1)

    # If too small, skip
    if w < 3 or h < 3:
        return None

    if direction == 'vertical':
        # Split x between x1+1 and x2-1
        split_x = random.randint(x1 + 1, x2 - 1)
        r1 = (x1, y1, split_x, y2)
        r2 = (split_x, y1, x2, y2)
        return (r1, r2)
    else:
        # Split y between y1+1 and y2-1
        split_y = random.randint(y1 + 1, y2 - 1)
        r1 = (x1, y1, x2, split_y)
        r2 = (x1, split_y, x2, y2)
        return (r1, r2)

def generate_floor(width=25, length=25, base_rooms=3,random_rooms=5,
                   min_ratio=0.05, max_ratio=0.40, max_ar=4.0):
    """
    Generates rooms with random splits:
      - Each room must meet area and aspect constraints (no discarding after).
      - Stops if it reaches (base_rooms + i) total rooms, i in [0..5].
    """
    total_a = width * length
    min_a = total_a * min_ratio
    max_a = total_a * max_ratio
    extra_rooms = random.randint(0, random_rooms)
    desired_rooms = base_rooms + extra_rooms

    rooms = [(0, 0, width, length)]

    attempts = 0
    # Attempt random splits
    for _ in range(50):
        attempts += 1
        if len(rooms) >= desired_rooms:
            break

        # Chooses a random room to devide
        idx = random.randint(0, len(rooms) - 1)
        old_room = rooms[idx]

        # Splits the room into two
        split_dir = random.choice(['vertical', 'horizontal'])
        new_rs = subdivide_room(old_room, split_dir)

        # If the new rooms were not generated, try again
        if new_rs is None:
            print("subdivision failed")
            break

        # Choose if the new rooms should replace the original or not
        r1, r2 = new_rs
        if room_conforms(r1, min_a, max_ar) and room_conforms(r2, min_a, max_ar):
            rooms.pop(idx)
            rooms.append(r1)
            rooms.append(r2)

    print (str(attempts) + " attempts in order to create " + str(desired_rooms) + " rooms")
    return rooms


def room_to_polygon(room):
    x1, y1, x2, y2 = room
    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

def plot_floor(rooms, ax):
    for room in rooms:
        poly = room_to_polygon(room)
        x, y = poly.exterior.xy
        ax.plot(x, y, color="black")

def style_axes(ax):
    # Make spines gray
    for spine in ax.spines.values():
        spine.set_color("gray")
        spine.set_bounds([0,25])
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    # Make ticks gray
    ax.tick_params(axis='x', colors='gray')
    ax.tick_params(axis='y', colors='gray')
    # Create a 5x5 grid
    ax.set_xticks(range(0, 26, 5))
    ax.set_yticks(range(0, 26, 5))
    ax.set_xlim(-1, 26)
    ax.set_ylim(-1, 26)
    ax.set_aspect("equal", "box")
    # Faded grid
    #ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)

def main():
    random.seed(42)
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))


    # Input parameters
    width = 25          # Total story width
    length = 25         # Total story heiht
    base_rooms = 6      # The least possible number of rooms    
    random_rooms = 3    # The upper limit of the aditional rooms. 
    min_ratio = 0.05            
    max_ratio = 0.4         
    max_ar = 3          

    for i in range(2):
        for j in range(4):
            ax = axes[i][j]
            rooms = generate_floor(width=width, length=length, base_rooms=base_rooms, random_rooms=random_rooms,
                                   min_ratio=min_ratio, max_ratio=max_ratio, max_ar=max_ar)
            columns = [(0, 0), (width, 0), (width, length), (0, length)]
            for col in columns:
                ax.plot(col[0], col[1], marker='s', color='crimson', markersize=4)
            plot_floor(rooms, ax)
            style_axes(ax)
            ax.set_title(f"Floor plan {i*4 + j+1}", color="gray")

    #plt.tight_layout()
    fig.subplots_adjust(wspace=0.4, hspace=0.4)
    os.makedirs("output", exist_ok=True)
    plt.savefig("output/multiple_floors.png", dpi=200)
    plt.close(fig)

if __name__ == "__main__":
    main()
