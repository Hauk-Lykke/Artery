from typing import List, Tuple, Protocol
import numpy as np
from src.components import Node, Room, Wall, AHU
from queue import PriorityQueue
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from math import atan2, pi

class Cost(ABC):
    @abstractmethod
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        pass

class MovementCost(Cost):
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        diff = np.abs(current - next)
        # Use Euclidean distance for more accurate diagonal costs
        return np.sqrt(np.sum(diff * diff))

class WallCrossingCost(Cost):
    def __init__(self, wall: Wall):
        self.wall = wall
        self.perpendicular_cost = 5.0
        self.angled_cost = 10.0
    
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

class WallProximityCost(Cost):
    def __init__(self, wall: Wall):
        self.wall = wall
        self.proximity_threshold = 1.0  # Distance at which wall proximity affects cost
        self.proximity_penalty = 2.0    # Penalty multiplier for being near walls
        
    def _point_to_line_distance(self, point: np.ndarray) -> float:
        """Calculate the shortest distance from a point to the wall segment"""
        wall_vec = self.wall.vector
        wall_len_sq = np.dot(wall_vec, wall_vec)
        if wall_len_sq == 0:
            return np.linalg.norm(point - self.wall.start)
        
        t = max(0, min(1, np.dot(point - self.wall.start, wall_vec) / wall_len_sq))
        projection = self.wall.start + t * wall_vec
        return np.linalg.norm(point - projection)
        
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        # Check proximity for both current and next positions
        current_dist = self._point_to_line_distance(current)
        next_dist = self._point_to_line_distance(next)
        
        cost = 0
        if current_dist < self.proximity_threshold:
            cost += (self.proximity_threshold - current_dist) * self.proximity_penalty
        if next_dist < self.proximity_threshold:
            cost += (self.proximity_threshold - next_dist) * self.proximity_penalty
            
        return cost

class CompositeCost(Cost):
    def __init__(self, costs: List[Tuple[Cost, float]]):
        self.costs = costs  # List of (cost, weight) tuples
    
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        return sum(weight * cost.calculate(current, next) for cost, weight in self.costs)

class Heuristic(ABC):
    @abstractmethod
    def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
        pass

class EuclideanDistance(Heuristic):
    def calculate(self, current: np.ndarray, goal: np.ndarray) -> float:
        diff = np.abs(current - goal)
        return np.sqrt(np.sum(diff * diff))

class WallCrossingHeuristic(Heuristic):
    def __init__(self, wall: Wall):
        self.wall = wall
        self.perpendicular_cost = 5.0
        self.angled_cost = 10.0
    
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
    def __init__(self, rooms: List[Room]):
        self.rooms = rooms
        
        # Create wall crossing costs and heuristics
        wall_costs = []
        wall_heuristics = []
        proximity_costs = []
        for room in rooms:
            for wall in room.walls:
                wall_costs.append((WallCrossingCost(wall), 0.5))
                wall_heuristics.append((WallCrossingHeuristic(wall), 0.5))
                proximity_costs.append((WallProximityCost(wall), 0.4))
        
        # Create composite cost with movement, wall crossings, and wall proximity
        self.composite_cost = CompositeCost([(MovementCost(), 1.0)] + wall_costs + proximity_costs)
        
        # Create composite heuristic with euclidean distance and wall crossings
        self.composite_h = CompositeHeuristic([(EuclideanDistance(), 1.0)] + wall_heuristics)
    
    def euclidean_distance(self, a: np.ndarray, b: np.ndarray) -> float:
        diff = np.abs(a - b)
        return np.sqrt(np.sum(diff * diff))

    def find_furthest_room(self, ahu: AHU) -> Room:
        return max(self.rooms, key=lambda room: self.euclidean_distance(room.center, ahu.position))

    def a_star(self, start: np.ndarray, goal: np.ndarray, 
               heuristic: Heuristic = None, cost: Cost = None, ax=None) -> Tuple[List[np.ndarray], List[float]]:
        if heuristic is None:
            heuristic = EuclideanDistance()
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
                costs = []
                while current_node:
                    path.append(current_node.position)
                    costs.append(current_node.g)
                    current_node = current_node.parent
                print(f"Path found in {iterations} iterations")
                return path[::-1], costs[::-1]
            
            closed_set.add(tuple(map(round, current_node.position)))
            
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]:
                neighbor_pos = current_node.position + np.array([dx, dy])
                
                if tuple(map(round, neighbor_pos)) in closed_set:
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
                    # Color the attempted nodes based on their cost
                    normalized_cost = neighbor.g / (neighbor.g + 1)  # Normalize to prevent division by zero
                    color = plt.cm.viridis(normalized_cost)
                    ax.plot(neighbor_pos[0], neighbor_pos[1], 'o', color=color, markersize=2)
                    # Add a longer pause every 10 iterations, otherwise use a small pause
                    plt.pause(0.1 if iterations % 10 == 0 else 0.001)
            
            if iterations % 100 == 0:
                print(f"Iteration {iterations}, current position: {current_node.position}, goal: {goal}")
        
        print(f"No path found from {start} to {goal} after {iterations} iterations")
        return [], []

    def create_direct_route(self, start: np.ndarray, end: np.ndarray) -> List[np.ndarray]:
        return [start, end]
