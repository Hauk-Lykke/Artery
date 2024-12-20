import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue
from src.components import AHU, Node, Room, Wall
from src.pathfinding import (
    Pathfinder, ManhattanDistance, MovementCost, 
    WallCrossingCost, CompositeCost
)

def find_closest_point_on_route(point: np.ndarray, route: List[np.ndarray]) -> np.ndarray:
    return min(route, key=lambda p: Pathfinder.manhattan_distance(point, p))

def create_branch_routes(rooms: List[Room], main_route: List[np.ndarray], composite_cost: CompositeCost = None) -> List[List[np.ndarray]]:
    branch_routes = []
    for room in rooms:
        closest_point = find_closest_point_on_route(room.center, main_route)
        manhattan = ManhattanDistance()
        cost = composite_cost if composite_cost else MovementCost()
        branch_route = Pathfinder.a_star(room.center, closest_point, rooms, manhattan, cost)
        branch_routes.append(branch_route)
    return branch_routes

def route_ducts(rooms: List[Room], ahu: AHU):
    furthest_room = Pathfinder.find_furthest_room(rooms, ahu)
    
    print(f"AHU position: {ahu.position}")
    print(f"Furthest room center: {furthest_room.center}")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    visualize_layout(rooms, ahu, ax)
    
    # Create manhattan distance heuristic
    manhattan_h = ManhattanDistance()
    
    # Create wall crossing costs for main walls
    wall_costs = []
    
    # Find vertical walls (x-aligned walls)
    x_coords = sorted(list(set(corner[0] for room in rooms for corner in room.corners)))
    for x in x_coords[1:-1]:  # Skip outer walls
        wall = Wall(np.array([x, 0]), np.array([x, max(corner[1] for room in rooms for corner in room.corners)]))
        wall_costs.append((WallCrossingCost(wall), 1.0))
    
    # Find horizontal walls (y-aligned walls)
    y_coords = sorted(list(set(corner[1] for room in rooms for corner in room.corners)))
    for y in y_coords[1:-1]:  # Skip outer walls
        wall = Wall(np.array([0, y]), np.array([max(corner[0] for room in rooms for corner in room.corners), y]))
        wall_costs.append((WallCrossingCost(wall), 1.0))
    
    # Create composite cost with movement and wall crossings
    composite_cost = CompositeCost([(MovementCost(), 1.0)] + wall_costs)
    
    # Create main route using A* with manhattan heuristic and composite cost
    index_route = Pathfinder.a_star(ahu.position, furthest_room.center, rooms, manhattan_h, composite_cost, ax=ax)
    
    # Create branch routes using same cost function
    other_rooms = [room for room in rooms if room != furthest_room]
    branch_routes = create_branch_routes(other_rooms, index_route, composite_cost)
    
    # Visualize all routes
    all_routes = [index_route] + branch_routes
    visualize_routing(all_routes, ax)
    
    plt.show()
    return all_routes

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
