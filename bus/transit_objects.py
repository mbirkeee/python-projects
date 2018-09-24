from modes import BUFFER_METHOD
from modes import BUFFER_LIST

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
        self._manually_removed_stops = []

        # The segments must be a list because the open data format currently
        # uses multiple segments to illustrate a route
        self._segments = []
        self._segment_dict = {}

    def set_name(self, name):
        self._name = name

    def set_stop_dict(self, stop_dict):
        self._stop_dict = stop_dict

    def get_stop_ids(self):
        return self._stop_ids

    def get_stops(self):
        result = []
        for stop_id in self._stop_ids:
            result.append(self._stop_dict.get(stop_id))
        return result

    def manually_add_stop(self, stop_id):
        self.add_stop_id(stop_id)

    def manually_remove_stop(self, stop_id):
        self._stop_ids.remove(stop_id)
        self._manually_removed_stops.append(stop_id)
        self._manually_removed_stops = list(set(self._manually_removed_stops))

    def get_stops_removed(self):
        result = []
        for stop_id in self._manually_removed_stops:
            stop = self._stop_dict.get(stop_id)
            result.append(stop)
        return result

    def get_stops_added(self):
        """
        Only return the stops that were manually added
        """
        result = []
        for stop_id in self._stop_ids:
            stop = self._stop_dict.get(stop_id)
            if stop.was_manually_added(self._route_id):
                result.append(stop)
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

    def __repr__(self):
         return "%3d: %s (%d)" % (self._route_number, self._name, self._route_id)

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

        # Record which routes this stop was manually added to
        self._manually_added_to_routes = []

        self._demand = 1.0

        self._attributes = {}

    def was_manually_added(self, route_id):
        if route_id in self._manually_added_to_routes:
            return True
        return False

    def manually_add_route(self, route_id):
        self.add_route_id(route_id)
        self._manually_added_to_routes.append(route_id)
        self._manually_added_to_routes = list(set(self._manually_added_to_routes))

    def manually_remove_route(self, route_id):
        if not route_id in self._serves_route_ids:
            raise ValueError("manually_remove_route: stop %d does not serve route %d" % \
                (self.get_id(), route_id))

        self._serves_route_ids.remove(route_id)
        try:
            self._manually_added_to_routes.remove(route_id)
        except:
            pass

    def make_buffer(self, buffer_method, buffer_manager=None):

        if buffer_method == BUFFER_METHOD.CIRCLE_400:
            self.make_round_buffer(400)
        elif buffer_method == BUFFER_METHOD.SQUARE_709:
            self.make_square_buffer(709)
        elif buffer_method == BUFFER_METHOD.DIAMOND_500:
            self.make_diamond_buffer(500)
        elif buffer_method == BUFFER_METHOD.NETWORK_400:
            self.make_network_buffer(400, buffer_manager)
        else:

            for method in BUFFER_LIST:
                print "Supported buffer method:", method
            raise ValueError("buffer method %s not supported" % buffer_method)


    def make_round_buffer(self, size):
        point = self.get_point()
        self._buffer_p = point.get_round_buffer(size)

    def make_square_buffer(self, size):
        point = self.get_point()
        self._buffer_p = point.get_square_buffer(size)

    def make_diamond_buffer(self, size):
        point = self.get_point()
        self._buffer_p = point.get_diamond_buffer(size)

    def make_network_buffer(self, size, buffer_man=None):
        my_id = self.get_id()
        self._buffer_p = buffer_man.get_buffer(my_id)

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

    def get_lat(self):
        return self._point.get_lat()

    def get_lng(self):
        return self._point.get_lng()

    def get_distance(self, stop, method="crow"):

        point = self.get_point()
        return point.get_distance(stop.get_point(), method=method)

    def add_route_id(self, route_id):

        self._serves_route_ids.append(route_id)
        self._serves_route_ids = list(set(self._serves_route_ids))

    def serves_route(self, route):
        if isinstance(route, TransitRoute):
            route_id = route.get_id()
        else:
            route_id = route

        if route_id in self._serves_route_ids:
            return True

        return False

    def get_route_ids(self):
        return self._serves_route_ids

    def get_buffer(self):
        return self._buffer_p

    def __repr__(self):
        result = []
        result.append("ID: %d: Serves routes: %s" % (self._stop_id, repr(self._serves_route_ids)))
        result.append("ID: %s Manually added to routes: %s" % (self._stop_id, repr(self._manually_added_to_routes)))
        return "\n".join(result)
