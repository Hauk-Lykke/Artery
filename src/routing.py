import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue
from src.components import AHU, Node, Room, Wall
from src.pathfinding import (
    Pathfinder, EuclideanDistance, MovementCost, 
    WallCrossingCost, CompositeCost
)

def route_ducts(rooms: List[Room], ahu: AHU):
    plt.ion()  # Turn on interactive mode
    pathfinder = Pathfinder(rooms)
    furthest_room = pathfinder.find_furthest_room(ahu)
    
    print(f"AHU position: {ahu.position}")
    print(f"Furthest room center: {furthest_room.center}")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    visualize_layout(rooms, ahu, ax)
    
    # Create route to the furthest room using A* with euclidean heuristic and composite cost
    index_route = pathfinder.a_star(ahu.position, furthest_room.center, pathfinder.euclidean_h, pathfinder.composite_cost, ax=ax)
    visualize_routing([index_route], ax)
    
    plt.show(block=True)
    plt.ioff()  # Turn off interactive mode after showing
    return [index_route], fig, ax

def visualize_layout(rooms: List[Room], ahu: AHU, ax):
    # Plot rooms
    for room in rooms:
        corners = np.vstack((room.corners, room.corners[0]))  # Close the polygon
        ax.plot(corners[:, 0], corners[:, 1], 'b-')
    
    # Plot AHU
    ax.plot(ahu.position[0], ahu.position[1], 'rs', markersize=10)
    
    # Plot room centers
    for room in rooms:
        ax.plot(room.center[0], room.center[1], 'go', markersize=5)
    
    ax.set_title("Building Layout and Duct Routing")
    ax.axis('equal')
    ax.grid(True)

def visualize_routing(routes: List[List[np.ndarray]], ax):
    # Plot routes
    for route in routes:
        route_array = np.array(route)
        ax.plot(route_array[:, 0], route_array[:, 1], 'r-', linewidth=2)
