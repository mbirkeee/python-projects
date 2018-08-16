import os
import shapefile
import time

from constants import KEY
from constants import SERVICE
from constants import MODE
from constants import BUFFER

from geometry import Polyline
from geometry import Point

from route_id_names import ROUTE_IDS_05_04
from route_id_names import ROUTE_IDS_06_21
from route_id_names import BAD_STOP_IDS_BRT
from route_id_names import BAD_SHAPES

from transit_trips import TransitTrips
from transit_shapes import TransitShapes

from transit_objects import TransitStop
from transit_objects import TransitRoute
from stop_times import StopTimes


MODE_DICT = {
    MODE.ONE : {
        KEY.BUFFER     : BUFFER.CIRCLE_400
    }
}

class TransitShapefile(object):
    """
    This manager processes the transit data as supplied in shapefiles (e.g., the BRT data)
    """
    def __init__(self, base_path):
        self._base_path = base_path

        self._route_dict = {}
        self._stop_dict = {}

        self._dir_dict = {
            "inbound"   : "IB",
            "outbound"  : "OB",
            "cw"        : "CW",
            "ccw"       : "CC"
        }

        self._active_stop_ids = []
        self._active_stops = []

        self.read_directions()
        self.read_stops()
        self.read_direction_stops()

        # After dictionaries built, cross-link them
        for route in self._route_dict.itervalues():
            route.set_stop_dict(self._stop_dict)

        for stop in self._stop_dict.itervalues():
            stop.set_route_dict(self._route_dict)

    def get_active_stops(self):
        if not self._active_stops:
            self.get_active_stop_ids()
        return self._active_stops

    def get_active_stop_ids(self):

        if not self._active_stop_ids:
            for stop_id, stop in self._stop_dict.iteritems():
                if len(stop.get_route_ids()) > 0:
                    self._active_stop_ids.append(stop_id)
                    self._active_stops.append(stop)

        return self._active_stop_ids

    def get_segments(self, route_id):
        route = self.get_route(route_id)
        return route.get_segments()

    # def get_polylines(self, route_id):
    #     """
    #     Return a list to be compatible with pre-brt data
    #     """
    #     p = Polyline()
    #     data = self._route_dict.get(route_id)
    #     points = data.get('points')
    #     for point in points:
    #         # print point.get_lat_lng()
    #         p.add_point(point)
    #
    #     print "BRT", route_id, p, len(p.get_points())
    #     return [p]

 #   def get_points(self, route_id):
 #       raise ValueError("fixme!!")

    def get_route(self, route_id):
        return self._route_dict.get(route_id)

    def get_stop(self, stop_id):
        return self._stop_dict.get(stop_id)

    def get_routes(self):
        return [route for route in self._route_dict.itervalues()]

    def get_route_stops(self, route_id):
        route = self.get_route(route_id)
        stop_ids = route.get_stop_ids()
        result = [self.get_stop(stop_id) for stop_id in stop_ids]
        return result

    def get_stops(self):
        return self.get_active_stops()

    def get_route_ids(self):
        result = [k for k in self._route_dict.iterkeys()]
        return result

    def get_route_name(self, route_id):
        route = self.get_route(route_id)
        return route.get_name()

    def get_route_number(self, route_id):
        route = self.get_route(route_id)
        return route.get_number()

    def read_directions(self):

        sf = shapefile.Reader("%s/directions.dbf" % self._base_path)

        records = sf.records()
        shapes = sf.shapes()

        # print "len(records)", len(records)
        # print "len(shapes)", len(shapes)

        for index, record in enumerate(records):
            shape = shapes[index]

#            print repr(record)
            # continue

            name = record[5].strip()

            space_pos = name.find(' ')
            route_number = int(name[:space_pos])
            name = name[space_pos:]

            d = record[2].strip().lower()

            direction = self._dir_dict.get(d)

            display_name = "%s (%s)" % (name.strip(), direction)
            route_id = int(record[1])

            if self._route_dict.has_key(route_id):
                raise ValueError("Already have route key")

            # points = [Point(p[1], p[0]) for p in shape.points]

            segment = Polyline()
            for p in shape.points:
                segment.add_point(Point(p[1], p[0]))

            route = TransitRoute(route_id, route_number, display_name)
            route.add_segment(segment)
            route.set_attribute(KEY.DIRECTION, direction)

            # self._data[route_id] = {
            #     'name'      : display_name,
            #     "direction" : direction,
            #     "points"    : points,
            #     "number"    : number,
            # }

            self._route_dict[route_id] = route

    def read_direction_stops(self):

        """
        ['1424e21', 'HDR Future Network V3', '4174', 'Superstore',
        "10 Mainline, Confederation - Centre Mall (Inbound),
        14 Crosstown, St Paul's (Outbound),
        3 BRT, Green (Inbound),
        48 Suburban Connector, 33rd St - Confed (Inbound)"]
        """
        line_count = 0

        # f = open("%s/test.out" % self._shape_base, 'rb')
        f = open("%s/direction_stops.dbf" % self._base_path, 'rb')
        for line in f:
            # print line
            line_count += 1
            if line_count > 2:
                print "line", line

            if line_count == 2:

                parts = line.split()

                part_count = len(parts)
                print "Total part count: %d" % len(parts)

                for i, part in enumerate(parts):
                    if i == 0 : continue

                    success = False
                    try:
                        float(part)
                        success = True
                    except:
                        if part.find("remix") >= 0:
                            success = True
                        elif part.find("Market") >= 0:
                            success = True
                        elif part.find("Mall") >= 0:
                            success = True
                    # print "%d part: '%s'" % (i, part)
                    # # if part.find("Market") >= 0:
                    # #     raise ValueError("here: %d" % i)
                    # if part.find("Lawson") >= 0:
                    #     raise ValueError("Lawson")

                    # if part.finf
                    # if i > 1010: break

                    if not success:
                        raise ValueError("Failed on part: %s" % part)

                part_index = 1

                while True:
                    if part_index >= part_count:
                        print "DONE"
                        break

                    route_id = int(parts[part_index].strip())

                    stop_id = parts[part_index + 1].strip()
                    if stop_id == "Market":
                        part_index += 1
                        stop_id = "Market Mall"
                    try:
                        stop_id = int(stop_id)
                    except:
                        print "Attempt to get stop_id from BAD_STOP_IDS", stop_id
                        stop_id = BAD_STOP_IDS_BRT.get(stop_id)

                    stop_id = int(stop_id)

                    stop = self._stop_dict.get(stop_id)
                    stop.add_route_id(route_id)

                    route = self._route_dict.get(route_id)
                    route.add_stop_id(stop_id)

                    dist = parts[part_index + 2].strip()

                    # print "dir_id", dir_id, "stop_id", stop_id, "dist", dist, self.get_route_name(dir_id)
                    part_index += 3

        f.close()

        for stop_id, stop in self._stop_dict.iteritems():
            print "Stop: %d Routes: %d" % (stop_id, len(stop.get_route_ids()))

        for route_id, route in self._route_dict.iteritems():
            print "Route: %d Name: %s Stops: %d" % (route.get_number(), route.get_name(), len(route.get_stop_ids()))

        print "number of routes", len(self._route_dict)

    def read_stops(self):

        file_name = "%s/stops.dbf" % self._base_path
        print "Reading stops file: %s" % file_name
        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        made_up_id = 10000

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for index, record in enumerate(records):
            # print repr(record)
            # continue

            shape = shapes[index]

            # print "len(shape.points)", len(shape.points)
            # print shape.points

            point = shape.points[0]
            lat = point[1]
            lng = point[0]

            stop_id = record[2]
            stop_name = record[3]
            lines = record[4]

            bad_id = None

            try:
                stop_id = int(stop_id)
            except:
                # print "'%s' : %d," % (record[2], made_up_id)
                # made_up_id += 1

                stop_id = BAD_STOP_IDS_BRT.get(record[2])
                if stop_id is None:
                    print "FAILED TO GET STOP ID for", record[2]
                    continue
                bad_id = record[2]

                #print "Error: Failed to get stop ID for:", record[2]


            # print stop_id, stop_name, lines
            # lines = lines.strip()
            # # print "LINES >>>%s<<<" % lines
            #
            # parts = lines.split(',')
            # # print "LINE PARTS:", len(parts)

            stop = TransitStop(stop_id, stop_name, Point(float(lat), float(lng)))

            if bad_id is not None:
                stop.set_attribute(KEY.BAD_ID, bad_id)

            if self._stop_dict.has_key(stop_id):
                raise ValueError("already have stop id: %s %d" % (repr(stop_id), index))

            self._stop_dict[stop_id] = stop

        for stop_id, stop in self._stop_dict.iteritems():
            point = stop.get_point()
            name = stop.get_name()
            print "stop_id: %d name: %s lat:%f lng: %f" % (stop_id, name, point.get_lat(), point.get_lng())

        print "Read %d stops" % len(self._stop_dict)


    def get_stop_points(self, route_id):

        result = []
        data = self._route_dict.get(route_id)
        stops = data.get("stops")
        for stop_id in stops:
            stop_data = self._stop_dict.get(stop_id)
            if stop_data is None:
                print "ERROR: no data for stop", repr(stop_id)
                continue

            point = stop_data.get('point')
            result.append(point)
        return result

class DataManager(object):
    """
    link_route_shapes : Get route shapes for plotting.  Not required for heatmap.
                        Speeds things up a little bit if skipped (OpenData only)

    link_stops        : Link stops to routes.  Required for heatmap but not for just
                        plotting the routes.  Speeds things up if skipped (OpenData only)
    """
    def __init__(self, base_path, link_route_shapes=False, link_stops=True):

        self._shapefile_mode = False

        if base_path.find("2018_05_04") > 0:
            print "this is the JUNE data"
            self._include_route_dict = ROUTE_IDS_05_04

        elif base_path.find('2018_08_05') > 0:
            print "this is the JULY data"
            self._include_route_dict = ROUTE_IDS_06_21

        else:
            self._shapefile_mode = True

        if self._shapefile_mode:
            self._shapefile = TransitShapefile(base_path)
        else:
            self._base_path = base_path
            self._route_dict = {}
            self._deprecated = {}
            self.read_file()

            self._stop_dict = {}
            self.read_file_stops()

            self._active_stops = []

            self._trips = TransitTrips(base_path)

            if link_route_shapes:
                self._shapes = TransitShapes(base_path)

                for route in self.get_routes():
                    shape_ids = self._trips.get_shape_ids(route.get_id())
                    for shape_id in shape_ids:
                        segment = self._shapes.get_polyline(shape_id)
                        route.add_segment(segment, segment_id=shape_id)

            # Must cross-link routes/stops before calling stop times
            # After dictionaries built, cross-link them
            for route in self._route_dict.itervalues():
                route.set_stop_dict(self._stop_dict)

            for stop in self._stop_dict.itervalues():
                stop.set_route_dict(self._route_dict)

            if link_stops:
                # This is SO ugly... must pass in reference to self
                self._stop_times = StopTimes(base_path, self)
                # self._trip_dict = {}
                # self._route_id_to_shape_id = {}
                # self.read_file_trips()

    def get_stops(self):
        if self._shapefile_mode:
            return self._shapefile.get_stops()
        return [stop for stop in self._stop_dict.itervalues()]

    def make_round_buffers(self, radius):
        stops = self.get_stops()
        for stop in stops:
            stop.make_round_buffer(radius)

    def get_active_stops(self):
        if self._shapefile_mode:
            return self._shapefile.get_active_stops()

        else:
            if not self._active_stops:
                stops = self.get_stops()
                for stop in stops:
                    routes_ids = stop.get_route_ids()
                    # print stop.get_name(), routes_ids
                    if len(routes_ids) > 0:
                        self._active_stops.append(stop)

        print "Total stops:", len(self._stop_dict)
        print "Active stops:", len(self._active_stops)
        return self._active_stops

    def get_route_from_trip_id(self, trip_id):

        route_id = self._trips.get_route_id(trip_id)
        return self.get_route(route_id)

    def get_trip_service_type(self, trip_id):
        return self._trips.get_service_type(trip_id)

    def get_trip_headsign(self, trip_id):
        return self._trips.get_headsign(trip_id)

    def get_trip_direction(self, trip_id):
        return self._trips.get_direction(trip_id)

    def read_file_stops(self):
        """
        0 stop_id,
        1 stop_code,
        2 stop_lat,
        3 stop_lon,
        4 location_type,
        5 wheelchair_boarding,
        6 name
        """
        file_name = os.path.join(self._base_path, "my-TransitStops.csv")

        result = {}
        line_count = 0
        f = None
        fake_stop_id = 10000

        print "Reading file %s..." % file_name

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                bad_id = None
                try:
                    item = parts[0].strip()
                    pos = item.find("_merged")
                    if pos > 0:
                        fixed = item[:pos]
                        print "Fixed :%s -> %s" % (item, fixed)
                        item = fixed

                    stop_id = int(item)

                except Exception as err:
                    print "Exception processing line: %s" % repr(err), item
                    print "Line: %s" % line
                    stop_id = fake_stop_id
                    print "Assign fake stop ID: %d" % fake_stop_id
                    fake_stop_id += 1
                    bad_id = item

                name = parts[6].strip()
                lat = float(parts[2].strip())
                lng = float(parts[3].strip())

                stop = TransitStop(stop_id, name, Point(lat, lng))
                if bad_id:
                    stop.set_attribute(KEY.BAD_ID, bad_id)

                result[stop_id] = stop

        finally:
            if f: f.close()

        self._stop_dict = result
        print "Read %d stops" % len(self._stop_dict)

    def read_file(self):
        """
        0 route_id,
        1 route_type,
        2 route_color,
        3 text_color,
        4 name_short,
        5 name_long
        """
        file_name = os.path.join(self._base_path, "my-TransitRoutes.csv")

        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                route_id = int(parts[0].strip())
                route_number = int(parts[4].strip())
                long_name = parts[5].strip()

                # I am not sure what the route type is
                route_type = int(parts[1].strip())

                if route_type != 3:
                    raise ValueError("route type not 3")

                print "read route ID", route_id

                if not self._include_route_dict.has_key(route_id):
                    print "SKIPPING ROUTE", route_id
                    self._deprecated[route_id] = (route_number, long_name)
                    continue

                if self._route_dict.has_key(route_id):
                    raise ValueError("THIS IS A DUP!!!")

                route = TransitRoute(route_id, route_number, long_name)

                # self._data[route_id] = (short_name, long_name)
                self._route_dict[route_id] = route

            print "number of routes:", len(self._route_dict)

        finally:
            if f:
                f.close()

        # ----- TEST -----
        s = []
        for route_id, route in self._route_dict.iteritems():
            name = route.get_name()
            s.append((name, route_id))

        s = sorted(s)
        for i, item in enumerate(s):
            print "%d ID: %s NAME: %s" % (i+1, item[1], item[0])
        # ---- END TEST -----

    # def get_stop_points(self, route_id):
    #     if self._shapefile_mode:
    #         return self._shapefile.get_stop_points(route_id)
    #     raise ValueError("fixme")

    # def get_stops(self, route_id):
    #     if self._shapefile_mode:
    #         return self._shapefile.get_stops(route_id)
    #     raise ValueError("fixme")

    def get_segments(self, route_id):
        """
        Unfortunately the pre-BRT data routes are described in not one but several polylines.
        These MUST be plotted independently otherwise we get lots of spurious lines on the plot
        :param route_id:
        :return:
        """
        if self._shapefile_mode:
            return self._shapefile.get_segments(route_id)

        # Allocate on demand
        if self._transit_trips is None:
            self._transit_trips = TransitTrips(self._base_path)

        # Allocate on demand
        if self._transit_shapes is None:
            self._transit_shapes = TransitShapes(self._base_path)

        result = []
        shape_ids = self._transit_trips.get_shape_ids(route_id)
        for shape_id in shape_ids:
            polyline = self._transit_shapes.get_polyline(shape_id)
            result.append(polyline)

        return result

    def get_route_ids(self):
        if self._shapefile_mode:
            return self._shapefile.get_route_ids()

        result = [k for k in self._route_dict.iterkeys()]
        return result

    def get_stop(self, stop_id):
        if self._shapefile_mode:
            return self._shapefile.get_stop(stop_id)
        return self._stop_dict.get(stop_id)

    def get_route(self, route_id):
        if self._shapefile_mode:
            return self._shapefile.get_route(route_id)
        return self._route_dict.get(route_id)

    def get_routes(self):
        if self._shapefile_mode:
            return self._shapefile.get_routes()

        return [route for route in self._route_dict.itervalues()]
