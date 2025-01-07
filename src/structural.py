from abc import ABC, abstractmethod
from src.core import Cost
from src.components import Wall, WallType
from src.geometry import line_intersection, point_to_line_distance, Point

class WallCrossingCost(Cost):
    """Base class for wall crossing costs"""
    def __init__(self, wall: Wall):
        self.wall = wall

class WallCosts:
    """Central definition of wall-related costs"""
    PROXIMITY_THRESHOLD = 0.5  # Distance at which wall proximity starts affecting cost
    ANGLE_MULTIPLIER = 2.0  # Multiplier for angled crossings
    
    @staticmethod
    def get_base_cost(wall_type: WallType) -> float:
        """Get the base perpendicular crossing cost for a wall type"""
        if wall_type == WallType.DRYWALL:
            return 1.0
        elif wall_type == WallType.CONCRETE:
            return 5.0
        else:  # OUTER_WALL
            return 20.0
    
    @staticmethod
    def get_angled_cost(wall_type: WallType) -> float:
        """Get the angled crossing cost for a wall type"""
        return WallCosts.get_base_cost(wall_type) * WallCosts.ANGLE_MULTIPLIER

class StandardWallCost(WallCrossingCost):
    """Standard implementation of wall crossing costs"""
    
    def __init__(self, wall: Wall):
        super().__init__(wall)
        self.perpendicular_cost = WallCosts.get_base_cost(wall.wall_type)
        self.angled_cost = WallCosts.get_angled_cost(wall.wall_type)
    
    def calculate(self, current: Point, next: Point) -> float:
        # Check if path crosses wall
        if line_intersection(current, next, self.wall.start, self.wall.end):
            path_vector = Point(next.x - current.x, next.y - current.y)
            angle = self.wall.get_angle_with(path_vector)
            angle = min(angle, 180 - angle)  # Normalize to 0-90 degrees
            return self.perpendicular_cost if abs(90 - angle) <= 3 else self.angled_cost
        
        # If not crossing, check proximity
        current_dist = point_to_line_distance(current, self.wall.start, self.wall.end)
        next_dist = point_to_line_distance(next, self.wall.start, self.wall.end)
        
        min_dist = min(current_dist, next_dist)
        if min_dist >= WallCosts.PROXIMITY_THRESHOLD:
            return 0.0
        
        # Linear interpolation between 0 and perpendicular_cost based on distance
        return self.perpendicular_cost * (1 - min_dist / WallCosts.PROXIMITY_THRESHOLD)
