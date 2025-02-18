import random
import math
import os
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Polygon

# ---------- Floor and Room Generation ----------

def area(room):
    '''
    Gives the area for a rectangular room.

    Parameters:
        room (tuple): Contains (x1, y1, x2, y2) coordinates for the room's corners.
    
    Returns:
        float: The total area.
    '''
    (x1, y1, x2, y2) = room
    return abs(x2 - x1) * abs(y2 - y1)

def aspect_ratio_ok(room, max_ar):
    '''
    Verifies that the aspect ratio is within a maximum limit.

    Parameters:
        room (tuple): Contains (x1, y1, x2, y2) coordinates for the room's corners.
        max_ar (float): Maximum allowable aspect ratio 
                        (long side divided by short side) for any room.

    Returns:
        bool: True if the aspect ratio is within the limit; False otherwise.
              Returns False if any side has zero length (invalid room).
    '''
    (x1, y1, x2, y2) = room
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    if min(w, h) == 0:
        return False
    return (max(w, h) / min(w, h)) <= max_ar

def room_conforms(room, min_a, max_a, max_ar):
    '''
    Verifies that a given room conforms to the area and aspect ratio constraints.

    Parameters:
        room (tuple): Contains (x1, y1, x2, y2) coordinates for the room's corners.
        min_a (float): Minimum allowable room area (absolute value).
        max_a (float): Maximum allowable room area (absolute value).
        max_ar (float): Maximum allowable aspect ratio for the room.
    
    Returns:
        bool: True if room conforms; False otherwise.
    '''
    a = area(room)
    if min_a <= a <= max_a:
        print(" ")
    else:
        print("fails! Area")

    if aspect_ratio_ok(room, max_ar):
        print(" ")
    else:
        print("fails! Aspect Ratio")
        print(" ")
    return (min_a <= a <= max_a) and aspect_ratio_ok(room, max_ar)

def subdivide_room(room, direction):
    '''
    Splits the room randomly in the specified direction.

    Parameters:
        room (tuple): The room to split (x1, y1, x2, y2).
        direction (str): 'vertical' or 'horizontal' split.
    
    Returns:
        tuple: A tuple containing two new room tuples, or None if the room is too small.
    '''
    (x1, y1, x2, y2) = room
    w = abs(x2 - x1)
    h = abs(y2 - y1)
    if w < 3 or h < 3:
        print("Room sides to shoort")
        return None

    if direction == 'vertical':
        split_x = random.randint(x1 + 1, x2 - 1)
        r1 = (x1, y1, split_x, y2)
        r2 = (split_x, y1, x2, y2)
        return (r1, r2)
    else:
        split_y = random.randint(y1 + 1, y2 - 1)
        r1 = (x1, y1, x2, split_y)
        r2 = (x1, split_y, x2, y2)
        return (r1, r2)

def generate_floor(width=25, length=25, random_rooms=2,
                   min_area=0.15, max_area=0.30, max_ar=3.0):
    """
    Generates a random floor layout by subdividing a rectangular floor plan into smaller rooms.

    Parameters:
        width (float or int): Overall width of the floor plan.
        length (float or int): Overall length of the floor plan.
        random_rooms (int): An upper limit for an additional random number of rooms.
                            The final room count is the minimum allowed number of rooms plus a random number between 0 and random_rooms.
        min_area (float):   Minimum allowable room area as a fraction of the total floor area.
        max_area (float):   Maximum allowable room area as a fraction of the total floor area.
        max_ar (float):     Maximum allowable aspect ratio (long side divided by short side) for any room.

    Returns:
        List of tuples: Each room is represented as a tuple (x1, y1, x2, y2), defining its bounding coordinates.

    Description:
        The function begins with a single room covering the entire floor plan.
        It computes the minimum allowed number of rooms based on the maximum allowed area:
            base_rooms = ceil(1 / max_area)
        (This is the fewest rooms required if every room is as large as allowed.)
        Then a random extra number of rooms (between 0 and random_rooms) is added to form the desired room count.
        The function repeatedly selects a random room and attempts to subdivide it (vertically or horizontally).
        A subdivision is accepted only if both resulting rooms meet the area and aspect ratio constraints.
        The process continues until the desired number of rooms is reached or a maximum number of iterations is exceeded.
    """
    total_area = width * length
    min_a = total_area * min_area
    max_a = total_area * max_area

    # Compute the minimum allowed number of rooms (if every room were at the maximum allowed area)
    base_rooms = math.ceil(1 / max_area)
    extra_rooms = random.randint(0, random_rooms)
    desired_rooms = base_rooms + extra_rooms

    print(f"Total floor area: {total_area} square meters")
    print(f"Each room must be between {min_a:.1f} and {max_a:.1f} square meters")
    print(f"Minimum allowed number of rooms based on max_area: {base_rooms}")
    print(f"Final base number of rooms: {desired_rooms}")
    print("")

    rooms = [(0, 0, width, length)]
    attempts = 0
    max_attempts = 10
    while attempts < max_attempts and len(rooms) < desired_rooms:
        attempts += 1
        idx = random.randint(0, len(rooms) - 1)
        old_room = rooms[idx]
        split_dir = random.choice(['vertical', 'horizontal'])
        new_rs = subdivide_room(old_room, split_dir)
        if new_rs is None:
            continue
        r1, r2 = new_rs
        if room_conforms(r1, min_a, max_a, max_ar) and room_conforms(r2, min_a, max_a, max_ar):
            rooms.pop(idx)
            rooms.append(r1)
            rooms.append(r2)
            '''
    if attempts == max_attempts:
        raise RuntimeError(
            "Number of iterations exceeded maximum allowed iterations. "
            "This is likely due to overconstraining the solution."
        )'''

    print(f"{attempts} iterations to create {len(rooms)} rooms")
    return rooms

def room_to_polygon(room):
    x1, y1, x2, y2 = room
    return Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

def plot_floor(rooms, ax):
    for room in rooms:
        poly = room_to_polygon(room)
        x, y = poly.exterior.xy
        ax.plot(x, y, color="black")

# ---------- Integration in Main ----------

def main():
    random.seed(42)
    width = 25
    length = 25
    random_rooms = 2
    min_area = 0.02
    max_area = 0.12
    max_ar = 2.4

    # Generate one floor plan.
    rooms = generate_floor(width=width, length=length, random_rooms=random_rooms,
                           min_area=min_area, max_area=max_area, max_ar=max_ar)
    
    # Plot the floor plan.
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_floor(rooms, ax)
    ax.set_title("Generated Floor Plan")
    ax.set_xlim(-1, width+1)
    ax.set_ylim(-1, length+1)
    ax.set_aspect("equal", "box")
    plt.show()

if __name__ == "__main__":
    main()
