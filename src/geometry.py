import numpy as np
from typing import Tuple

def line_intersection(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray, p4: np.ndarray) -> bool:
    """Check if line segments (p1,p2) and (p3,p4) intersect."""
    def ccw(A: np.ndarray, B: np.ndarray, C: np.ndarray) -> bool:
        val = (C[1] - A[1]) * (B[0] - A[0]) - (B[1] - A[1]) * (C[0] - A[0])
        if abs(val) < 1e-10:  # Points are collinear
            return False
        return val > 0
    return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))

def point_to_line_distance(point: np.ndarray, line_start: np.ndarray, line_end: np.ndarray) -> float:
    """Calculate the shortest distance from a point to a line segment"""
    line_vec = line_end - line_start
    line_len_sq = np.dot(line_vec, line_vec)
    if line_len_sq == 0:
        return np.linalg.norm(point - line_start)
    
    t = max(0, min(1, np.dot(point - line_start, line_vec) / line_len_sq))
    projection = line_start + t * line_vec
    return np.linalg.norm(point - projection)
