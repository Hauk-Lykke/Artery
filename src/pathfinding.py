from typing import List, Tuple
import numpy as np
from src.components import Node, Room
from queue import PriorityQueue
import matplotlib as plt

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

def a_star(start: np.ndarray, goal: np.ndarray, obstacles: List[Room], ax=None) -> List[np.ndarray]:
    start_node = Node(start)
    end_node = Node(goal)
    
    open_list = PriorityQueue()
    open_list.put((0, start_node))
    closed_set = set()
    
    iterations = 0
    max_iterations = 1000
    
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
        
        if iterations % 100 == 0:
            print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
    
    print(f"No path found from {start} to {goal} after {iterations} iterations")
    return []

def manhattan_distance(a: np.ndarray, b: np.ndarray) -> float:
    return np.sum(np.abs(a - b))

def find_furthest_room(rooms: List[Room], ahu: AHU) -> Room:
    return max(rooms, key=lambda room: manhattan_distance(room.center, ahu.position))

def create_direct_route(start: np.ndarray, end: np.ndarray) -> List[np.ndarray]:
    return [start, end]
