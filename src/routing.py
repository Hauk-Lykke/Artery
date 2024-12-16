import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue
from src.components import AHU, Node, Room
import pathfinding as pf # import a_star, manhattan_distance, create_direct_route, find_furthest_room

def find_closest_point_on_route(point: np.ndarray, route: List[np.ndarray]) -> np.ndarray:
    return min(route, key=lambda p: pf.manhattan_distance(point, p))

def create_branch_routes(rooms: List[Room], main_route: List[np.ndarray]) -> List[List[np.ndarray]]:
    branch_routes = []
    for room in rooms:
        closest_point = find_closest_point_on_route(room.center, main_route)
        branch_route = pf.create_direct_route(room.center, closest_point)
        branch_routes.append(branch_route)
    return branch_routes

def route_ducts(rooms: List[Room], ahu: AHU):
    furthest_room = pf.find_furthest_room(rooms, ahu)
    
    print(f"AHU position: {ahu.position}")
    print(f"Furthest room center: {furthest_room.center}")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    visualize_layout(rooms, ahu, ax)
    
    # Create a direct route to the furthest room
    index_route = pf.create_direct_route(ahu.position, furthest_room.center)
    visualize_routing([index_route], ax)
    
    plt.show()
    return [index_route]

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

