import os
import math

from my_utils import Weight
from my_utils import is_shapefile
from geometry import Point
from geometry import Polygon

from data_manager import TransitShapefile
from transit_objects import TransitStop

from constants import KEY

class TransitStopsObsolete(object):

    def __init__(self, base_path):

        self._base_path = base_path
        self._shapefile_mode = False
        self._weight = Weight()

        if is_shapefile(self._base_path):
            self._shapefile_mode = True
            self._shapefile = TransitShapefile(base_path)
        else:
            self._stop_dict = {}
            self.read_file_stops()

    # def read_file_stops(self):
    #     """
    #     0 stop_id,
    #     1 stop_code,
    #     2 stop_lat,
    #     3 stop_lon,
    #     4 location_type,
    #     5 wheelchair_boarding,
    #     6 name
    #     """
    #     file_name = os.path.join(self._base_path, "my-TransitStops.csv")
    #
    #     result = {}
    #     line_count = 0
    #     f = None
    #     fake_stop_id = 10000
    #
    #     try:
    #         f = open(file_name, 'r')
    #
    #         for line in f:
    #             line_count += 1
    #             if line_count == 1: continue
    #
    #             line = line.strip()
    #             parts = line.split(",")
    #
    #             bad_id = None
    #             try:
    #                 item = parts[0].strip()
    #                 stop_id = int(item)
    #
    #             except Exception as err:
    #                 print "Exception processing line: %s" % repr(err), item
    #                 print "line: %s" % line
    #                 stop_id = fake_stop_id
    #                 print "Assign fake stop ID: %d" % fake_stop_id
    #                 fake_stop_id += 1
    #                 bad_id = item
    #
    #             name = parts[6].strip()
    #             lat = float(parts[2].strip())
    #             lng = float(parts[3].strip())
    #
    #             stop = TransitStop(stop_id, name, Point(lat, lng))
    #             if bad_id:
    #                 stop.set_attribute(KEY.BAD_ID, bad_id)
    #
    #             result[stop_id] = stop
    #
    #     finally:
    #         if f: f.close()
    #
    #     self._stop_dict = result
    #     print "Read %d stops" % len(self._stop_dict)

    def get_name(self, stop_id):
        # print "Getting STOP name for stop id", stop_id

        stop_data = self.get_stop_data(stop_id)
        if stop_data is None:
            return None

        return stop_data.get('name')

    def get_point(self, stop_id):

        stop_data = self.get_stop_data(stop_id)
        if stop_data is None:
            return None

        return stop_data.get('point')

    def get_active_stops(self):
        if self._shapefile_mode:
            return self._shapefile.get_active_stops()

        print "NOTE!!!! THIS DOES NOT YET CHECK FOR ACTIVE STOPS!!!!!"
        return [stop for stop in self._stop_dict.itervalues()]

    def get_ids(self):
        if self._shapefile_mode:
            return self._shapefile.get_active_stop_ids()

        result = [stop_id for stop_id in self._stop_dict.iterkeys()]
        return result

    def get_stop_data(self, stop_id):
        if self._shapefile_mode:
            return self._shapefile.get_stop_data(stop_id)

        return self._stop_dict.get(stop_id)

    def get_buffer(self, stop_id):

        stop_data = self.get_stop_data(stop_id)
        if stop_data is None:
            return None

        return stop_data.get('buffer')

    def make_round_buffers(self, size):
        stops = self.get_active_stops()
        for stop in stops:
            stop.make_round_buffer(size)

    def make_square_buffers(self, size):

        half = float(size)/2.0
        corners = [
            (-half,  half),
            ( half,  half),
            ( half, -half),
            (-half, -half),
        ]

        for stop_id, stop_data in self._stop_dict.iteritems():
            # print "Making buffer for stop_id: %d" % stop_id
            point = stop_data.get('point')
            # print repr(point)
            p = Polygon()
            for corner in corners:
                p.add_point(Point(point.get_x() + corner[0], point.get_y() + corner[1]))

            stop_data['buffer'] = p

    def get_buffer_polygons(self):
        result = {}
        stop_ids = self.get_ids()
        for stop_id in stop_ids:
            stop_data = self.get_stop_data(stop_id)
            result[stop_id] = stop_data.get('buffer')
        return result

    def get_demand(self, stop_id):
        stop_data = self.get_stop_data(stop_id)
        return stop_data.get('demand')

    def compute_demand(self, intersect, das):

        stop_ids = self.get_ids()
        for stop_id in stop_ids:
            # for stop_id, stop_data in self._data.iteritems():
            # print "compute demand for stop id", stop_id

            stop_point = self.get_point(stop_id)
            demand = 0

            # group1: da_ids, group2: stop_ids
            intersecting_das = intersect.get_intersections(group=2, id=stop_id)
            for item in intersecting_das:
                p = item[0]
                da_id = item[1]
                da_area = das.get_area(da_id)
                intersect_area = p.get_area()
                area_factor = intersect_area / da_area
                population = das.get_population(da_id)
                intersect_centroid = p.get_centroid()
                intersect_distance = stop_point.get_distance(intersect_centroid)
                intersect_population = population * area_factor
                butterworth = self._weight.butterworth(intersect_distance)

                # print "  intersects %s" % da_id
                # print "    da area:             ", da_area
                # print "    intersect area:      ", intersect_area
                # print "    area factor:         ", area_factor
                # print "    population           ", population
                # print "    intersect population ", intersect_population
                # print "    distance             ", intersect_distance
                # print "    butterworth          ", butterworth

                demand += butterworth * intersect_population

            stop_data = self.get_stop_data(stop_id)
            stop_data['demand'] = demand
            print "Demand for stop %d: %f" % (stop_id, demand)
