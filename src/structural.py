from abc import ABC, abstractmethod
import numpy as np
from src.core import Cost
from src.components import Wall, WallType

class WallCrossingCost(Cost):
    """Base class for wall crossing costs"""
    def __init__(self, wall: Wall):
        self.wall = wall
    
    def _line_intersection(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> bool:
        """Check if line segments (p1,p2) and (p3,p4) intersect."""
        def ccw(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
            val = (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
            if abs(val) < 1e-10:  # Points are collinear
                return False
            return val > 0
        return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))
    
    def _point_to_line_distance(self, point: np.ndarray) -> float:
        """Calculate the shortest distance from a point to the wall segment"""
        wall_vec = self.wall.vector
        wall_len_sq = np.dot(wall_vec, wall_vec)
        if wall_len_sq == 0:
            return np.linalg.norm(point - self.wall.start)
        
        t = max(0, min(1, np.dot(point - self.wall.start, wall_vec) / wall_len_sq))
        projection = self.wall.start + t * wall_vec
        return np.linalg.norm(point - projection)

class StandardWallCost(WallCrossingCost):
    """Standard implementation of wall crossing costs"""
    PROXIMITY_THRESHOLD = 0.5  # Distance at which wall proximity starts affecting cost
    
    def __init__(self, wall: Wall):
        super().__init__(wall)
        if wall.wall_type == WallType.DRYWALL:
            self.perpendicular_cost = 1.0
        elif wall.wall_type == WallType.CONCRETE:
            self.perpendicular_cost = 5.0
        else:  # OUTER_WALL
            self.perpendicular_cost = 15.0
        self.angled_cost = 2 * self.perpendicular_cost
    
    def calculate(self, current: np.ndarray, next: np.ndarray) -> float:
        # Check if path crosses wall
        if self._line_intersection(current, next, self.wall.start, self.wall.end):
            path_vector = next - current
            angle = self.wall.get_angle_with(path_vector)
            angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
            return self.perpendicular_cost if abs(90 - angle) <= 3 else self.angled_cost
        
        # If not crossing, check proximity
        current_dist = self._point_to_line_distance(current)
        next_dist = self._point_to_line_distance(next)
        
        min_dist = min(current_dist, next_dist)
        if min_dist >= self.PROXIMITY_THRESHOLD:
            return 0.0
        
        # Linear interpolation between 0 and perpendicular_cost based on distance
        return self.perpendicular_cost * (1 - min_dist / self.PROXIMITY_THRESHOLD)
