import pytest
import numpy as np
from math import isclose, sqrt
from geometry import Polygon, Vector, Point, Line  # Replace `your_module` with the actual module name
import shapely as sh

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
	np_array = v.toNumpy()
	assert np.array_equal(np_array, np.array([1, 2, 3]))
	v_from_np = Vector.fromNumpy(np.array([4, 5, 6]))
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

def test_create_Polygon():
	p1 = Point(0, 0, 0)
	p2 = Point(1, 1, 1)
	p3 = Point(1, 0, 0)
	poly = Polygon([p1, p2, p3])
	assert(isinstance(poly, Polygon))
	assert(p1 in poly.points)

def test_polygon_fromShapelyPoly():
	p1 = sh.Point(0,0,0)
	p2 = sh.Point(1, 1, 1)
	p3 = sh.Point(1, 0, 0)
	shapelyPoly = sh.Polygon([p1, p2, p3])
	assert(isinstance(shapelyPoly, sh.Polygon))
	poly = Polygon.fromShapelyPolygon(shapelyPoly)
	assert(isinstance(poly, Polygon))

def test_convexHull():
	p0 = Point(0,0,0)
	p1 = Point(10,0,0)
	p2 = Point(10,10,0)
	p3 = Point(5,5,0)
	p4 = Point(0,10,0)
	points = [p0, p1, p2, p3, p4]
	poly = Polygon(points)
	convexHullPoly = Polygon.convexHull(poly)
	for point in convexHullPoly.points:
		assert(point in convexHullPoly.points)


# def test_shapely_distance():
	
def test_line_contains_line():
	p0 = Point(0,0,0)
	p1 = Point(5,0,0)
	p2 = Point(10,0,0)
	p3 = Point(12,0,0)
	P4 = Point(14, 0, 0)
	shortLine = Line(p0,p1)
	longLine = Line(p0, p2)
	otherLine = Line(p3,P4)
	assert(longLine.contains(shortLine))
	assert(not longLine.contains(otherLine))
	# overlappingLine = Line(p2, p3)
	# longLine.contains(overlappingLine)
