import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from queue import PriorityQueue
from src.components import AHU, Node, Room, Wall
from src.pathfinding import (
	Pathfinder, EuclideanDistance, MovementCost, 
	WallProximityCost, CompositeCost
)
from src.visualization import visualize_layout, visualize_routing

def route_ducts(rooms: List[Room], ahu: AHU):
	pathfinder = Pathfinder(rooms)
	furthest_room = pathfinder.find_furthest_room(ahu)
	
	print(f"AHU position: {ahu.position}")
	print(f"Furthest room center: {furthest_room.center}")
	
	fig, ax = plt.subplots(figsize=(12, 8))
	visualize_layout(rooms, ahu, ax)
	
	# Create route to the furthest room using A* with composite heuristic and cost
	index_route, costs = pathfinder.a_star(ahu.position, furthest_room.center, pathfinder.composite_h, pathfinder.composite_cost, ax=ax)
	visualize_routing([(index_route, costs)], ax)
	
	plt.draw()
	plt.show(block=True)  # This will keep the window open even if the test fails
	return [(index_route, costs)], fig, ax
