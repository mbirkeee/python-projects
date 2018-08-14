import math

from geometry import Polygon
from geometry import Point

from intersect import Intersect

class TransitRoute(object):
    """
    A single transit route
    """
    def __init__(self, route_id, route_number, name):
        self._route_id = route_id
        self._name = name
        self._route_number = route_number
        self._stop_ids = []
        self._attributes = {}
        self._stop_dict = None

        # The segments must be a list because the open data format currently
        # uses multiple segments to illustrate a route
        self._segments = []
        self._segment_dict = {}

    def set_stop_dict(self, stop_dict):
        self._stop_dict = stop_dict

    def get_stop_ids(self):
        return self._stop_ids

    def get_stops(self):
        result = []
        for stop_id in self._stop_ids:
            result.append(self._stop_dict.get(stop_id))
        return result

    def get_id(self):
        return self._route_id

    def add_segment(self, segment, segment_id=None):
        self._segments.append(segment)
        if segment_id is not None:
            self._segment_dict[segment_id] = segment

    def get_segments(self):
        return self._segments

    def get_segments_dict(self):
        return self._segment_dict

    def set_attribute(self, key, value):
        self._attributes[key] = value

    def get_number(self):
        return self._route_number

    def get_name(self):
        return self._name

    def add_stop_id(self, stop_id):
        if stop_id is None:
            raise ValueError("Stop ID is NONE!!")

        self._stop_ids.append(stop_id)
        self._stop_ids = list(set(self._stop_ids))

class TransitStop(object):
    """
    A Single transit stop
    """
    def __init__(self, stop_id, name, point):

        self._stop_id = stop_id
        self._name = name
        self._point = point
        self._serves_route_ids = []
        self._buffer_p = None
        self._route_dict = None
        self._demand = 1.0

        self._attributes = {}

    def make_round_buffer(self, size):
        point = self.get_point()
        self._buffer_p = point.get_round_buffer(size)

    def compute_demand(self, intersect, filter):

        demand = 0
        stop_point = self.get_point()

        intersecting_das = intersect.get_intersections(group=1, id=self.get_id())
        print "this stop intersects %d das" % len(intersecting_das)
        for item in intersecting_das:
            p = item[0]
            da = item[2]
            area_factor = p.get_area() / da.get_area()
            population = da.get_population()
            intersect_centroid = p.get_centroid()
            intersect_distance = stop_point.get_distance(intersect_centroid)
            intersect_population = population * area_factor
            weight = filter.run(intersect_distance)
            demand += weight * intersect_population

        self._demand = demand
        print "Demand for stop %d: %f" % (self.get_id(), demand)

    def get_demand(self):
        return self._demand

    def get_polygon(self):
        return self._buffer_p

    def set_route_dict(self, route_dict):
        self._route_dict = route_dict

    def get_routes(self):
        result = []
        for route_id in self._serves_route_ids:
            route = self._route_dict.get(route_id)
            result.append(route)
        return result

    def get_id(self):
        return self._stop_id

    def set_attribute(self, key, value):
        self._attributes[key] = value

    def get_name(self):
        return self._name

    def get_point(self):
        return self._point

    def add_route_id(self, route_id):

        self._serves_route_ids.append(route_id)
        self._serves_route_ids = list(set(self._serves_route_ids))

    def get_route_ids(self):
        return self._serves_route_ids

    def get_buffer(self):
        return self._buffer_p