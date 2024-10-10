import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue

class Room:
    def __init__(self, corners: List[Tuple[float, float]]):
        self.corners = np.array(corners)
        self.center = np.mean(corners, axis=0)

class AHU:
    def __init__(self, position: Tuple[float, float]):
        self.position = np.array(position)

class Node:
    def __init__(self, position: np.ndarray, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def manhattan_distance(a: np.ndarray, b: np.ndarray) -> float:
    return np.sum(np.abs(a - b))

def a_star(start: np.ndarray, goal: np.ndarray, obstacles: List[Room], ax=None) -> List[np.ndarray]:
    start_node = Node(start)
    end_node = Node(goal)
    
    open_list = PriorityQueue()
    open_list.put((0, start_node))
    closed_set = set()
    
    iterations = 0
    max_iterations = 1000  # Increased max iterations
    
    while not open_list.empty() and iterations < max_iterations:
        iterations += 1
        current_node = open_list.get()[1]
        
        if np.allclose(current_node.position, end_node.position, atol=0.5):
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            print(f"Path found in {iterations} iterations")
            return path[::-1]
        
        closed_set.add(tuple(map(round, current_node.position)))
        
        for dx, dy in [(0, 0.5), (0.5, 0), (0, -0.5), (-0.5, 0)]:
            neighbor_pos = current_node.position + np.array([dx, dy])
            
            if tuple(map(round, neighbor_pos)) in closed_set:
                continue
            
            if any(point_in_room(neighbor_pos, room) for room in obstacles):
                if ax:
                    ax.plot(neighbor_pos[0], neighbor_pos[1], 'rx', markersize=3)
                plt.pause(0.001)  # Add a small pause to update the plot
                continue
            
            neighbor = Node(neighbor_pos, current_node)
            neighbor.g = current_node.g + manhattan_distance(current_node.position, neighbor_pos)
            neighbor.h = manhattan_distance(neighbor_pos, end_node.position)
            neighbor.f = neighbor.g + neighbor.h
            
            open_list.put((neighbor.f, neighbor))
            
            if ax:
                ax.plot(neighbor_pos[0], neighbor_pos[1], 'go', markersize=2)
                plt.pause(0.001)  # Add a small pause to update the plot
        
        if iterations % 1000 == 0:
            print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
    
    print(f"No path found from {start} to {goal} after {iterations} iterations")
    return []

def point_in_room(point: np.ndarray, room: Room) -> bool:
    x, y = point
    n = len(room.corners)
    inside = False
    p1x, p1y = room.corners[0]
    for i in range(n + 1):
        p2x, p2y = room.corners[i % n]
        if y > min(p1y, p2y) - 0.3:
            if y <= max(p1y, p2y) + 0.3:
                if x <= max(p1x, p2x) + 0.3:
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters + 0.3:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def find_furthest_room(rooms: List[Room], ahu: AHU) -> Room:
    return max(rooms, key=lambda room: manhattan_distance(room.center, ahu.position))

def route_ducts(rooms: List[Room], ahu: AHU):
    furthest_room = find_furthest_room(rooms, ahu)
    
    print(f"AHU position: {ahu.position}")
    print(f"Furthest room center: {furthest_room.center}")
    
    fig, ax = plt.subplots(figsize=(12, 8))
    visualize_layout(rooms, ahu, ax)
    
    # Route to the furthest room
    route = a_star(ahu.position, furthest_room.center, [r for r in rooms if r != furthest_room], ax)
    if route:
        visualize_routing([route], ax)
        plt.pause(0.5)  # Pause to show the route
    else:
        print("Failed to route to the furthest room")
    
    plt.show()
    return [route] if route else []

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
        ax.plot(route_array[:, 0], route_array[:, 1], 'g-', linewidth=2)

# Example usage with adjacent rooms
rooms = [
    Room([(0, 0), (0, 5), (5, 5), (5, 0)]),
    Room([(5, 0), (5, 5), (10, 5), (10, 0)]),
    Room([(0, 5), (0, 10), (5, 10), (5, 5)]),
    Room([(5, 5), (5, 10), (10, 10), (10, 5)])
]
ahu = AHU((2.5, 2.5))  # AHU position adjusted to be within the bottom-left room

routes = route_ducts(rooms, ahu)
if not routes:
    print("Failed to generate routes")
