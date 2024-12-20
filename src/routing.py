import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue
from src.components import AHU, Node, Room, Wall
from src.pathfinding import (
    Pathfinder, EuclideanDistance, MovementCost, 
    WallCrossingCost, WallProximityCost, CompositeCost
)

def route_ducts(rooms: List[Room], ahu: AHU):
    plt.ion()  # Turn on interactive mode
    pathfinder = Pathfinder(rooms)
    furthest_room = pathfinder.find_furthest_room(ahu)
    
    print(f"AHU position: {ahu.position}")
    print(f"Furthest room center: {furthest_room.center}")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    visualize_layout(rooms, ahu, ax)
    
    # Create route to the furthest room using A* with composite heuristic and cost
    index_route, costs = pathfinder.a_star(ahu.position, furthest_room.center, pathfinder.composite_h, pathfinder.composite_cost, ax=ax)
    visualize_routing([(index_route, costs)], ax)
    
    plt.show(block=True)
    plt.ioff()  # Turn off interactive mode after showing
    return [(index_route, costs)], fig, ax

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

def visualize_routing(routes: List[Tuple[List[np.ndarray], List[float]]], ax):
    # Plot routes with color grading based on cost
    for route, costs in routes:
        route_array = np.array(route)
        points = route_array[:-1]  # All points except the last
        next_points = route_array[1:]  # All points except the first
        
        # Normalize costs for color mapping
        max_cost = max(costs)
        normalized_costs = np.array(costs[:-1]) / max_cost if max_cost > 0 else np.zeros_like(costs[:-1])
        
        # Create line segments colored by cost
        for i in range(len(points)):
            color = plt.cm.morgenstemning(normalized_costs[i])  # Use morgenstemning colormap
            ax.plot([points[i][0], next_points[i][0]], 
                   [points[i][1], next_points[i][1]], 
                   c=color, linewidth=2)
    
    # Add colorbar
    sm = plt.cm.ScalarMappable(cmap=plt.cm.morgenstemning, norm=plt.Normalize(vmin=0, vmax=max_cost))
    plt.colorbar(sm, ax=ax, label='Path Cost')
