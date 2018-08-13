import pyproj
import math
import ogr


PROJ = pyproj.Proj("+init=EPSG:32613")

class Point(object):

    def __init__(self, x, y):

        if x > 1000.0:
            # Assume this is UTM (Saskatoon)
            self._utm_x = x
            self._utm_y = y

            lng, lat = PROJ(x, y, inverse=True)

            self._lng = lng
            self._lat = lat

        else:
            self._lat = x
            self._lng = y

            utm_x, utm_y = PROJ(self._lng, self._lat)

            self._utm_x = utm_x
            self._utm_y = utm_y

    def get_lat(self):
        return self._lat

    def get_lng(self):
        return self._lng

    def get_lat_lng(self):
        return (self._lat, self._lng)

    def get_x(self):
        return self._utm_x

    def get_y(self):
        return self._utm_y

    def get_utm(self):
        return (self._utm_x, self._utm_y)

    def get_square_buffer(self, size):

        half = float(size)/2.0
        corners = [
            (-half,  half),
            ( half,  half),
            ( half, -half),
            (-half, -half),
        ]

        p = Polygon()
        for corner in corners:
            p.add_point(Point(self.get_x() + corner[0], self.get_y() + corner[1]))

        return p

    def get_round_buffer(self, size):

        x = self.get_x()
        y = self.get_y()

        p = Polygon()
        for i in xrange(360/10):
            r = math.radians(i * 10)
            p.add_point(Point(x + size * math.sin(r), y + size * math.cos(r)))

        return p

    def get_distance(self, point, method='crow'):

        x1 = self.get_x()
        y1 = self.get_y()
        x2 = point.get_x()
        y2 = point.get_y()

        return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2), 2))


class Polyline(object):

    def __init__(self):

        self._points = []
        self._attributes = {}

    def add_point(self, point):
        self._points.append(point)

    def get_points(self):
        return self._points

    def set_attribute(self, key, value):
        self._attributes[key] = value

    def get_attribute(self, key, default=None):
        return self._attributes.get(key, default)

class Polypoint(Polyline):
    pass

class Polygon(object):

    def __init__(self):
        self._points = []
        self._attributes = {}
        self._area = None
        self._centroid = None
        self._ogr_poly = None
        self._depth_count = 0
        self._temp_intersect = []
        self._raster_points = None
        self._raster_index = 0

    def set_area(self, area):
        """
        To be used only to override area (e.g., DA polygons)
        """
        self._area = area

    def add_point(self, point):
        self._points.append(point)

    def get_points(self):
        return self._points

    def set_attribute(self, key, value):
        self._attributes[key] = value

    def get_attribute(self, key, default=None):
        return self._attributes.get(key, default)

    # def compute_area(self, x, y):
    #     return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    def get_area(self):
        if self._area is None:

            # x = [point.get_x() for point in self._points]
            # y = [point.get_y() for point in self._points]
            # self._area = self.compute_area(x, y)

            ogr_poly = self.get_ogr_poly()
            self._area = ogr_poly.Area()

        # print "Area test", self._area, area2
        return self._area

    def get_ogr_poly(self):

        if self._ogr_poly is None:

            # Create ring
            ring = ogr.Geometry(ogr.wkbLinearRing)

            start_point = None

            for point in self._points:
                if start_point is None:
                    start_point = point

                ring.AddPoint(point.get_x(), point.get_y())

            # My polygons do not repeat the start point as the end point... but org ones do
            ring.AddPoint(start_point.get_x(), start_point.get_y())

            # Create polygon
            poly = ogr.Geometry(ogr.wkbPolygon)
            poly.AddGeometry(ring)

            self._ogr_poly = poly

        return self._ogr_poly

    def overlap(self, polygon):

        ogr_poly_1 = self.get_ogr_poly()
        ogr_poly_2 = polygon.get_ogr_poly()
        result = ogr_poly_1.Overlaps(ogr_poly_2)
        # print "Overlap result", repr(result)
        return result

    def touches(self, polygon):
        ogr_poly_1 = self.get_ogr_poly()
        ogr_poly_2 = polygon.get_ogr_poly()
        return ogr_poly_1.Touches(ogr_poly_2)

    def intersects(self, polygon):
        ogr_poly_1 = self.get_ogr_poly()
        ogr_poly_2 = polygon.get_ogr_poly()
        return ogr_poly_1.Intersects(ogr_poly_2)

    def intersect(self, polygon):

        org_poly_1 = self.get_ogr_poly()
        org_poly_2 = polygon.get_ogr_poly()

        intersection = org_poly_1.Intersection(org_poly_2)

        #print dir(org_poly_1)
        # raise ValueError("temp stop")
        # print "==================================="

        self._depth_count = 0
        self._temp_intersect = []

        # try:
        #     self._process_intersection(intersection)
        # except Exception as err:
        #     print "ERROR:", repr(err)

        self._process_intersection(intersection)
        # print "-----------------------------------"
        #return intersection
        return self._temp_intersect

    def get_centroid(self):

        if self._centroid is None:
            org_poly = self.get_ogr_poly()
            org_point = org_poly.Centroid()

            point_count = org_point.GetPointCount()
            if point_count != 1:
                raise ValueError("unexpected point count: %d" % point_count)

            pt = org_point.GetPoint(0)
            self._centroid = Point(pt[0], pt[1])

        return self._centroid

    def _process_intersection(self, intersection):
        """
        Recursive function to find polygons in the resulting intersection
        """
        if intersection is None:
            # print "intersection is none"
            return

        self._depth_count += 1
        # print "DEPTH COUNT", self._depth_count

        geometry_count = intersection.GetGeometryCount()
        name = intersection.GetGeometryName()

        # print "count", geometry_count, "name", name

        if name == 'POLYGON':
            if geometry_count != 1:
                raise ValueError("what the????")
            # print "found a POLYGON"
            thing = intersection.GetGeometryRef(0)
            point_count = thing.GetPointCount()
            # print "point count", point_count, thing.GetGeometryName()

            if point_count == 0:
                raise ValueError("point count is 0")
                # print "ERROR!!!!! point ccount is 0!!!!"
            else:
                p = Polygon()
                for j in xrange(point_count):
                    # GetPoint returns a tuple not a Geometry
                    pt = thing.GetPoint(j)
                    # print "%i). POINT (%d %d)" %(j, pt[0], pt[1])
                    p.add_point(Point(pt[0], pt[1]))
                self._temp_intersect.append(p)

        elif name == 'MULTIPOLYGON':
            # print "found a MULTIPOLYGON"
            for i in xrange(geometry_count):
                feature = intersection.GetGeometryRef(i)
                self._process_intersection(feature)

            # feature_count = intersection.GetGeometryCount()
        elif name == 'GEOMETRYCOLLECTION':
            pass
            # print "HOW TO HANDLE GEOMETRY COLLECTION?????"
        else:
            raise ValueError("cant handle name: %s" % name)

        self._depth_count -= 1
        return

        # print "intersection type:", type(intersection)
        # print "ExportTowkt:", repr(intersection.ExportToWkt())
        # print "intersection.GetGeometryCount()", intersection.GetGeometryCount()
        # print "intersection.GetGeometryName()", intersection.GetGeometryName()

    def get_raster_points(self, size):

        if self._raster_points is None:

            self._raster_points = []

            ogr_poly = self.get_ogr_poly()
            envelope = ogr_poly.GetEnvelope()

            start_x = 100 * int( envelope[0] / 100.0 ) - size
            start_y = 100 * int( envelope[2] / 100.0 ) - size

            end_x = 100 * int( envelope[1] / 100.0 ) + 2 * size
            end_y = 100 * int( envelope[3] / 100.0 ) + 2 * size

            # print "GET RASTER", start_x, start_y, end_x, end_y

            i = 0
            while True:
                x = start_x + i * size
                if x >= end_x: break

                j = 0
                while True:
                    y = start_y + j * size
                    if y > end_y : break

                    self._raster_points.append(Point(x, y))

                    j += 1

                i += 1

        return self._raster_points

