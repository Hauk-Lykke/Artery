from typing import List, Tuple, Protocol
import numpy as np
from src.components import Node, Room, Wall, AHU
from queue import PriorityQueue
import matplotlib as plt
from abc import ABC, abstractmethod
from math import atan2, pi

class Cost(ABC):
    @abstractmethod
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        pass

class MovementCost(Cost):
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        return np.sum(np.abs(current - next))

class WallCrossingCost(Cost):
    def __init__(self, wall: Wall):
        self.wall = wall
        self.perpendicular_cost = 3.0
        self.angled_cost = 7.0
    
    def _line_intersection(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> bool:
        """Check if line segments (p1,p2) and (p3,p4) intersect"""
        def ccw(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
            val = (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
            if abs(val) < 1e-10:  # Points are collinear
                return False
            return val > 0
        return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))
    
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        if not self._line_intersection(current, next, self.wall.start, self.wall.end):
            return 0.0
        
        path_vector = next - current
        angle = self.wall.get_angle_with(path_vector)
        angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
        return self.perpendicular_cost if abs(90 - angle) <= 5 else self.angled_cost

class CompositeCost(Cost):
    def __init__(self, costs: List[Tuple[Cost, float]]):
        self.costs = costs  # List of (cost, weight) tuples
    
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        return sum(weight * cost.calculate(current, next) for cost, weight in self.costs)

class Heuristic(ABC):
    @abstractmethod
    def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
        pass

class ManhattanDistance(Heuristic):
    def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
        return np.sum(np.abs(current - goal))

class WallCrossingHeuristic(Heuristic):
    def __init__(self, wall: Wall):
        self.wall = wall
        self.perpendicular_cost = 3.0
        self.angled_cost = 7.0
    
    def _line_intersection(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> bool:
        """Check if line segments (p1,p2) and (p3,p4) intersect"""
        def ccw(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
            # Handle collinear points
            val = (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
            if abs(val) < 1e-10:  # Points are collinear
                return False
            return val > 0

        # Check if line segments intersect
        return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))
    
    def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
        path_vector = goal - current
        
        if not self._line_intersection(current, goal, self.wall.start, self.wall.end):
            return 0.0
            
        # Calculate angle between path vector and wall
        angle = self.wall.get_angle_with(path_vector)
        
        # Normalize angle to be between 0 and 90 degrees
        angle = min(angle, 180 - angle)
        
        # Return cost based on crossing angle
        return self.perpendicular_cost if abs(90 - angle) <= 5 else self.angled_cost

class CompositeHeuristic(Heuristic):
    def __init__(self, heuristics: List[Tuple[Heuristic, float]]):
        self.heuristics = heuristics  # List of (heuristic, weight) tuples
        
    def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
        return sum(weight * h.calculate(current, goal) for h, weight in self.heuristics)

class Pathfinder:
    @staticmethod
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

    @staticmethod
    def manhattan_distance(a: np.ndarray, b: np.ndarray) -> float:
        return np.sum(np.abs(a - b))

    @classmethod
    def a_star(cls, start: np.ndarray, goal: np.ndarray, obstacles: List[Room], 
               heuristic: Heuristic = None, cost: Cost = None, ax=None) -> List[np.ndarray]:
        if heuristic is None:
            heuristic = ManhattanDistance()
        if cost is None:
            cost = MovementCost()
            
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
                
                # Skip positions inside rooms
                if any(cls.point_in_room(neighbor_pos, room) for room in obstacles):
                    continue
                
                neighbor = Node(neighbor_pos, current_node)
                
                # Calculate g cost using provided cost function
                g_cost = cost.calculate(current_node.position, neighbor_pos)
                neighbor.g = current_node.g + g_cost
                
                # Calculate h cost using provided heuristic
                neighbor.h = heuristic.calculate(neighbor_pos, end_node.position)
                neighbor.f = neighbor.g + neighbor.h
                
                open_list.put((neighbor.f, neighbor))
                
                if ax:
                    ax.plot(neighbor_pos[0], neighbor_pos[1], 'go', markersize=2)
                    plt.pause(0.001)  # Add a small pause to update the plot
            
            if iterations % 100 == 0:
                print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
        
        print(f"No path found from {start} to {goal} after {iterations} iterations")
        return []

    @classmethod
    def find_furthest_room(cls, rooms: List[Room], ahu: AHU) -> Room:
        return max(rooms, key=lambda room: cls.manhattan_distance(room.center, ahu.position))

    @staticmethod
    def create_direct_route(start: np.ndarray, end: np.ndarray) -> List[np.ndarray]:
        return [start, end]
