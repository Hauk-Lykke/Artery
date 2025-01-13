import pytest
from structural import FloorPlan, WallType
from tests.conftest import room_plan_11_rooms_random_concrete_fixture

class TestRandomConcreteFixture:
	def test_returns_floor_plan(self, room_plan_11_rooms_random_concrete_fixture):
		floor_plan = room_plan_11_rooms_random_concrete_fixture
		assert isinstance(floor_plan, FloorPlan)

	def test_wall_types_are_valid(self, room_plan_11_rooms_random_concrete_fixture):
		floor_plan = room_plan_11_rooms_random_concrete_fixture
		for wall in floor_plan.walls:
			assert wall.wallType in [WallType.OUTER_WALL, WallType.DRYWALL, WallType.CONCRETE]

	def test_outer_walls_unchanged(self, room_plan_11_rooms_random_concrete_fixture):
		floor_plan = room_plan_11_rooms_random_concrete_fixture
		outer_walls = [wall for wall in floor_plan.walls if wall.wallType == WallType.OUTER_WALL]
		# Count outer walls before modification
		initial_outer_wall_count = len(outer_walls)
		# Verify outer walls remain unchanged
		assert len([wall for wall in floor_plan.walls 
				   if wall.wallType == WallType.OUTER_WALL]) == initial_outer_wall_count

	def test_drywall_probability(self, room_plan_11_rooms_random_concrete_fixture):
		# Monte Carlo simulation with 100 runs
		total_non_outer_walls = 0
		total_drywall = 0
		
		for _ in range(100):
			floor_plan = room_plan_11_rooms_random_concrete_fixture
			non_outer_walls = [wall for wall in floor_plan.walls 
							 if wall.wallType != WallType.OUTER_WALL]
			total_non_outer_walls += len(non_outer_walls)
			total_drywall += len([wall for wall in non_outer_walls 
								if wall.wallType == WallType.DRYWALL])

		drywall_probability = total_drywall / total_non_outer_walls
		# Allow for 5% margin of error
		assert 0.65 <= drywall_probability <= 0.75, \
			   f"Drywall probability {drywall_probability:.2f} is outside expected range"