import math

from geometry import Point
from geometry import Polygon

lat_start = 52.125
lng_start = -106.65

point1 = Point(lat_start, lng_start)

x = point1.get_x()
y = point1.get_y()

point2 = Point(x+100, y)

print "test distance", point1.get_distance(point2)

lat2 = point2.get_lat()
lng2 = point2.get_lng()

lng_diff2 = lng_start - lng2
lat_diff2 = lat_start - lat2

print "lng2", lng_diff2
print "lat2", lat_diff2

lng_corr = math.sqrt(lng_diff2 * lng_diff2 + lat_diff2 * lat_diff2)

point3 = Point(x, y+100)

lat3 = point3.get_lat()
lng3 = point3.get_lng()

lng_diff3 = lng_start - lng3
lat_diff3 = lat_start - lat3

lat_corr = math.sqrt(lng_diff3 * lng_diff3 + lat_diff3 * lat_diff3)

print "lng3", lng_diff3
print "lat3", lat_diff3

print "BEFORE CORRECTION"

polygon1 = Polygon()
polygon1.add_point(Point(lat_start,             lng_start))
polygon1.add_point(Point(lat_start,             lng_start + lng_diff2))
polygon1.add_point(Point(lat_start + lat_diff3, lng_start + lng_diff2))
polygon1.add_point(Point(lat_start + lat_diff3, lng_start))

print "area", polygon1.get_area()

print "AFTER CORRECTION"

polygon1 = Polygon()
polygon1.add_point(Point(lat_start,             lng_start))
polygon1.add_point(Point(lat_start,             lng_start + lng_corr))
polygon1.add_point(Point(lat_start + lat_corr,  lng_start + lng_corr))
polygon1.add_point(Point(lat_start + lat_corr, lng_start))

print "area", polygon1.get_area()

print "lng_corr", lng_corr
print "lat_corr", lat_corr

polygon1 = Polygon()
polygon1.add_point(Point(lat_start,             lng_start))
polygon1.add_point(Point(lat_start,             lng_start + .00146))
polygon1.add_point(Point(lat_start + .000899,     lng_start + .00146))
polygon1.add_point(Point(lat_start + .000899,     lng_start))
print "Final", polygon1.get_area()

lng_c2 = .00146049608306
lat_c2 = .00089893575680

point1 = Point(lat_start, lng_start)
point2 = Point(lat_start, lng_start + lng_c2)
print "Distance", point1.get_distance(point2)

point1 = Point(lat_start, lng_start)
point2 = Point(lat_start + lat_c2, lng_start)
print "Distance", point1.get_distance(point2)


polygon1 = Polygon()
polygon1.add_point(Point(lat_start,             lng_start))
polygon1.add_point(Point(lat_start,             lng_start + lng_c2))
polygon1.add_point(Point(lat_start + lat_c2,     lng_start +lng_c2))
polygon1.add_point(Point(lat_start + lat_c2,     lng_start))
print "Final", polygon1.get_area()
