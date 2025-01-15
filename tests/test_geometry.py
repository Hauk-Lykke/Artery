import pytest
import numpy as np
from math import isclose, sqrt
from geometry import PolyLine, Vector, Point, Line  # Replace `your_module` with the actual module name

def test_vector_initialization():
	v1 = Vector(1, 2, 3)
	assert v1.x == 1
	assert v1.y == 2
	assert v1.z == 3

def test_vector_operations():
	v1 = Vector(1, 2, 3)
	v2 = Vector(2, 3, 4)
	v_add = v1 + v2
	assert v_add == Vector(3, 5, 7)
	v_sub = v1 - v2
	assert v_sub == Vector(-1, -1, -1)

def test_vector_equality():
	v1 = Vector(1, 2, 3)
	v2 = Vector(1, 2, 3)
	assert v1 == v2

def test_vector_hash():
	v1 = Vector(1, 2, 3)
	v2 = Vector(1, 2, 3)
	assert hash(v1) == hash(v2)

def test_vector_numpy_conversion():
	v = Vector(1, 2, 3)
	np_array = v.to_numpy()
	assert np.array_equal(np_array, np.array([1, 2, 3]))
	v_from_np = Vector.from_numpy(np.array([4, 5, 6]))
	assert v_from_np == Vector(4, 5, 6)

def test_vector_angle():
	v1 = Vector(1, 0, 0)
	v2 = Vector(0, 1, 0)
	angle = v1.getAngleWith(v2)
	assert isclose(angle, 90.0, abs_tol=1e-5)

def test_point_initialization():
	p = Point(1, 2, 3)
	assert p.x == 1
	assert p.y == 2
	assert p.z == 3

def test_line_initialization():
	p1 = Point(0, 0, 0)
	p2 = Point(1, 1, 1)
	line = Line(p1, p2)
	assert line.start == p1
	assert line.end == p2

def test_line_intersection():
	p1 = Point(0, 0, 0)
	p2 = Point(1, 1, 0)
	p3 = Point(0, 1, 0)
	p4 = Point(1, 0, 0)
	line1 = Line(p1, p2)
	line2 = Line(p3, p4)
	line3 = Line(p1,p3)
	line4 = Line(p2,p4)
	assert line1.intersects(line2)
	assert not line3.intersects(line4)

def test_line_distance_to_point():
	p1 = Point(0, 0, 0)
	p2 = Point(1, 1, 1)
	p3 = Point(1, 0, 0)
	line = Line(p1, p2)
	distance = line.distanceTo(p3)
	assert isclose(distance, sqrt(2) / 2, abs_tol=1e-5)

if __name__ == "__main__":
	pytest.main()

def test_make_PolyLine():
	segment0 = Line(Point(0,0,0),Point(1,1,0))
	segment1 = Line(Point(1,1,0),Point(2,1,0))
	polyLine = PolyLine([segment0, segment1])

def test_simplify_PolyLine():
	segment0 = Line(Point(0,0,0),Point(1,1,0))
	segment1 = Line(Point(1,1,0),Point(2,1,0))
	polyLine = PolyLine([segment0, segment1])
	polyLine.simplify(tolerance=0.5)
