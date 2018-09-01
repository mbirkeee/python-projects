import os
import shapefile
import time

from constants import KEY

from geometry import Polyline
from geometry import Point

from dataset import SERVICE, SERVICES
from dataset import BAD_STOP_IDS_BRT
from dataset import DATASETS
from dataset import OPEN_DATA_ROUTE_FILTER

from stop_updates import STOP_UPDATES

from transit_trips import TransitTrips
from transit_shapes import TransitShapes

from transit_objects import TransitStop
from transit_objects import TransitRoute
from stop_times import StopTimes

from brt_schedule import BRT_SCHEDULE

class BrtSchedule(object):

    def __init__(self, get_route_callback):

#        self._dataman = dataman
        self._data = {}
        self._get_route_callback = get_route_callback

        for key, value in BRT_SCHEDULE.iteritems():
            # print key, value

            # Convert the keys from entered to internal
            data = {
                SERVICE.MWF : value.get('m'),
                SERVICE.SAT : value.get('sa'),
                SERVICE.SUN : value.get('sn'),
            }

            data = self._init_times(data)

            # Since the entered dict keys specify multiple routes, this makes a copy
            # for each route
            key_parts = key.split(",")
            for part in key_parts:
                route_number = int(part.strip())

                self._data[route_number] = data

        # for key, value in self._data.iteritems():
        #     print "KEY", key, "VALUE", repr(value)

    def _convert_times(self, data):

        result = []
        if data is None:
            return

        for item in data:
            # The items are tuples of format (start_time, end_time, minutes_between departures)
            # All times are even hours that is, ints)

            item_new = (item[0] * 60, (item[1] * 60) - 1, item[2])
            # print "fix", item, "--->", item_new

            result.append(item_new)

        return result

    def _init_times(self, data):
        # print "convert times for", repr(data)
        for service in SERVICES:
            data[service] = self._convert_times(data.get(service))
        return data

    def _get_time_minutes(self, time_str):

        parts = time_str.split(":")
        if len(parts) == 1:
            # This is just an hour specification
            result = 60 * int(parts[0])
        elif len(parts) == 2:
            result = 60 * int(parts[0]) + int(parts[1])
        else:
            raise ValueError("Invalid time string: %s" % repr(time_str))

        # print "time: %s --> %d" % (time_str, result)
        return result

    def _get_route_number(self, route):

        # Handle passed in routes or route_ids
        if isinstance(route, int):
            route = self._get_route_callback(route)
        return route.get_number()

    def _find_tuples(self, route_number, service):

        data = self._data.get(route_number)
        if data is None:
            raise ValueError("Cant find data for route: %s" % repr(route_number))
        return data.get(service)

    def _find_tuple(self, route_number, service, minutes):

        data = self._data.get(route_number)
        if data is None:
            raise ValueError("Cant find data for route: %s" % repr(route_number))
        s = data.get(service)

        if not s:
            return

        for item in s:
            # print "Consider item", item
            if minutes >= item[0] and minutes <= item[1]:
                return item

    def get_departs_per_hour(self, route, service, time_str):
        t = self._get_time_minutes(time_str)
        route_number = self._get_route_number(route)

        item = self._find_tuple(route_number, service, t)
        if item is None:
            return 0

        # print "Found tuple", item
        result = 60.0 / float(item[2])
        return result

    def get_departs_per_day(self, route, service):
        route_number = self._get_route_number(route)
        tuples = self._find_tuples(route_number, service)
        if tuples is None:
            return 0

        total = 0.0
        for item in tuples:
            # print "depart per day process item:", item
            total += (float(item[1]) - float(item[0])) / float(item[2])

        return total

    def get_departs_per_week(self, route):
        total = self.get_departs_per_day(route, SERVICE.MWF)
        total += self.get_departs_per_day(route, SERVICE.SAT)
        total += self.get_departs_per_day(route, SERVICE.SUN)
        return total

    def get_depart_wait_minutes(self, route, service, time_str):
        t = self._get_time_minutes(time_str)
        route_number = self._get_route_number(route)

        item = self._find_tuple(route_number, service, t)
        if item is None:
            return None

        # print "Found tuple", item
        # Item 2 is the departure frequency in minutes...
        # so average wait time is frequency/2
        result = float(item[2])/2.0
        return result

class DatamanBase(object):

    def __init__(self, dataset):

        self._base_path = DATASETS.get(dataset)

        self._route_dict = {}
        self._stop_dict = {}

    def get_depart_wait_minutes(self, route, direction, stop_id, service, time_str):
        raise NotImplementedError

    def get_departs_per_hour(self, route, direction, stop_id, service, time_str):
        raise NotImplementedError

    def get_departs_per_day(self, route, direction, stop_id, service):
        raise NotImplementedError

    def get_departs_per_week(self, route, direction, stop_id):
        raise NotImplementedError

    def get_segments(self, route_id):
        raise NotImplementedError

    def get_stops(self):
        raise NotImplementedError

    def get_route_ids(self):
        raise NotImplementedError

    # def get_stop(self, stop_id):
    #     raise NotImplementedError

    # def get_route(self, route_id):
    #     raise NotImplementedError

    # def get_routes(self):
    #     raise NotImplementedError

    def make_round_buffers(self, radius):
        stops = self.get_stops()
        for stop in stops:
            stop.make_round_buffer(radius)

    def get_route(self, route_id):
        return self._route_dict.get(route_id)

    def get_stop(self, stop_id):
        return self._stop_dict.get(stop_id)

    def get_route_ids(self):
        result = [k for k in self._route_dict.iterkeys()]
        return result

    def get_routes(self):
        return [route for route in self._route_dict.itervalues()]

    def get_stops(self):
        return [stop for stop in self._stop_dict.itervalues()]

    def get_route_name(self, route_id):
        route = self.get_route(route_id)
        return route.get_name()

    def get_route_number(self, route_id):
        route = self.get_route(route_id)
        return route.get_number()

class DatamanBrt(DatamanBase):
    """
    This manager processes the transit data as supplied in shapefiles (e.g., the BRT data)
    """
    def __init__(self, dataset):

        super(DatamanBrt, self).__init__(dataset)

        print "TransitShapefile: %s" % self._base_path

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

        self._created_stop_id_base = 20000

        self.apply_stop_updates(dataset)

        self._schedule = BrtSchedule(self.get_route)

        # After dictionaries built, cross-link them
        for route in self._route_dict.itervalues():
            route.set_stop_dict(self._stop_dict)

        for stop in self._stop_dict.itervalues():
            stop.set_route_dict(self._route_dict)

    def get_depart_wait_minutes(self, route, direction, stop_id, service, time_str):
        if direction != 0: return None
        return self._schedule.get_depart_wait_minutes(route, service, time_str)

    def get_departs_per_hour(self, route, direction, stop_id, service, time_str):
        if direction != 0: return None
        return self._schedule.get_departs_per_hour(route, service, time_str)

    def get_departs_per_day(self, route, direction, stop_id, service):
        if direction != 0: return None
        return self._schedule.get_departs_per_day(route, service)

    def get_departs_per_week(self, route, direction, stop_id):
        if direction != 0: return None
        return self._schedule.get_departs_per_week(route)

    def apply_stops_added(self, added_stops, route_id):

        route = self._route_dict.get(route_id)

        for added_stop in added_stops:
            print "CONSIDER ADDED STOP", added_stop
            stop_id = added_stop.get(KEY.STOP_ID)

            if stop_id is None:
                print "THIS MUST BE A LAT/LON stop!!!!"
                lat = added_stop.get(KEY.LAT)
                lng = added_stop.get(KEY.LNG)
                if lat is None or lng is None:
                    raise ValueError("Bad Stop!")

                stop_id = self._created_stop_id_base
                self._created_stop_id_base += 1

                name = "Manually Created stop: %s" % repr(stop_id)
                stop = TransitStop(stop_id, name, Point(lat, lng))

                if self._stop_dict.has_key(stop_id):
                    raise ValueError("Duplicate stop_id!!!! %s" % repr(stop_id))

                self._stop_dict[stop_id] = stop

            else:
                print "Want to assign an existing stop to this route"
                stop = self._stop_dict.get(stop_id)

            # Assign this existing stop to the route
            stop.manually_add_route(route_id)
            route.manually_add_stop(stop_id)

            print repr(stop)

    def apply_stops_removed(self, removed_stops, route_id):

        route = self._route_dict.get(route_id)

        for removed_stop in removed_stops:
            stop_id = removed_stop.get(KEY.STOP_ID)

            stop = self._stop_dict.get(stop_id)
            if stop is None:
                raise ValueError("Bad stop!! stop_id: %s" % repr(stop_id))

            stop.manually_remove_route(route_id)
            route.manually_remove_stop(stop_id)

    def apply_stop_updates(self, dataset):

        stop_updates = STOP_UPDATES.get(dataset, [])

        for item in stop_updates:
            route_id = item.get(KEY.ROUTE_ID)
            print "Considering route:", route_id

            added_stops = item.get(KEY.STOPS_ADDED)
            self.apply_stops_added(added_stops, route_id)

            removed_stops = item.get(KEY.STOPS_REMOVED)
            self.apply_stops_removed(removed_stops, route_id)

            route_name = item.get(KEY.NAME)
            if route_name is not None:
                route = self.get_route(route_id)
                route.set_name(route_name)

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

#    def get_stop(self, stop_id):
#        return self._stop_dict.get(stop_id)

#    def get_routes(self):
#        return [route for route in self._route_dict.itervalues()]

    def get_route_stops(self, route_id):
        route = self.get_route(route_id)
        stop_ids = route.get_stop_ids()
        result = [self.get_stop(stop_id) for stop_id in stop_ids]
        return result

#    def get_stops(self):
#        return [stop for stop in self._stop_dict.itervalues()]

#    def get_route_ids(self):
#        result = [k for k in self._route_dict.iterkeys()]
#        return result


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
        file_name = "%s/direction_stops.dbf" % self._base_path
        print "Reading file: %s..." % file_name

        f = open(file_name, 'rb')
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

        # for stop_id, stop in self._stop_dict.iteritems():
        #     print "Stop: %d Routes: %d" % (stop_id, len(stop.get_route_ids()))

        for route_id, route in self._route_dict.iteritems():
            print "Route: %d Name: %s Stops: %d" % (route.get_number(), route.get_name(), len(route.get_stop_ids()))

        print "Total number of routes", len(self._route_dict)
        print "Done reading %s" % file_name

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

def dataman_factory(dataset, link_route_shapes=False, link_stops=True):
    base_path = DATASETS.get(dataset)
    if base_path is None:
        raise ValueError("dataset not supported: %s" % repr(dataset))

    include_data_dict = OPEN_DATA_ROUTE_FILTER.get(dataset)

    if include_data_dict is None:
        thing = DatamanBrt(dataset)
    else:
        thing = DataManagerOpen(dataset, link_route_shapes=link_route_shapes, link_stops=link_stops)

    return thing

class DataManagerOpen(DatamanBase):
    """
    link_route_shapes : Get route shapes for plotting.  Not required for heatmap.
                        Speeds things up a little bit if skipped (OpenData only)

    link_stops        : Link stops to routes.  Required for heatmap but not for just
                        plotting the routes.  Speeds things up if skipped (OpenData only)
    """
    def __init__(self, dataset, link_route_shapes=False, link_stops=True):

        super(DataManagerOpen, self).__init__(dataset)

        self._include_route_dict = OPEN_DATA_ROUTE_FILTER.get(dataset)

        self._deprecated = {}
        self.read_file()

        self.read_file_stops()
        self._active_stops = []

        self._trips = TransitTrips(self._base_path)

        if link_route_shapes:
            self._shapes = TransitShapes(self._base_path)

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
            self._stop_times = StopTimes(self._base_path, self)

    def _sanity_check_departures(self, stop_id, departures):
        """
        Look for departures on same route/stop but with different directions

        RESULT: There do not appear to be any cases where there is a departure
        from a stop on the same route but with a different direction
        """
        print "SANITY START"
        d = {}
        for depart in departures:
            # print repr(depart)
            direction = depart.get(KEY.DIRECTION)
            route_id = depart.get(KEY.ROUTE_ID)
            depart_time = depart.get(KEY.DEPART_TIME)

            key = "%d-%d" % (route_id, depart_time)
            # key = route_id

            have_direction = d.get(key)

            # print "HAVE", repr(have_direction), route_id
            if have_direction is not None and have_direction != direction:
                stop = self.get_stop(stop_id)
                route = self.get_route(route_id)
                print "WARN_DUPLICATE: %d (%s) %d (%s) " % (stop_id, stop.get_name(), route_id, route.get_name())
                # raise ValueError("different direction stop_id: %d route_id: %d!!!" % \
                #                   (stop_id, route_id))

            # print "setting %d to %d" % (route_id, direction)
            d[key] = direction

        print "SANITY DONE"

    def _get_time_minutes(self, time_str):

        parts = time_str.split(":")
        if len(parts) == 1:
            # This is just an hour specification
            result = 60 * int(parts[0])
        elif len(parts) == 2:
            result = 60 * int(parts[0]) + int(parts[1])
        else:
            raise ValueError("Invalid time string: %s" % repr(time_str))

        # print "time: %s --> %d" % (time_str, result)
        return result

    def _dump_data(self, departures):
        for depart in departures:
            print repr(depart)

        raise ValueError("ERROR")

    def get_departures(self, stop_id, service):
        return self._stop_times.get_stop_departures(stop_id, service)

    # def get_departs_per_hour(self, route, direction, stop_id, service, time_str):
    #     departs_0 = self._get_departs_per_hour_internal(route, stop_id, service, time_str, 0)
    #     departs_1 = self._get_departs_per_hour_internal(route, stop_id, service, time_str, 1)
    #
    #     return departs_0 + departs_1

    def get_departs_per_hour(self, route, direction, stop_id, service, time_str, ):
        """
        We must consider each diretion seperately
        """
        if isinstance(route, TransitRoute):
            route_id = route.get_id()
        else:
            route_id = route

        # Get target depart time
        target_sec = 60.0 * self._get_time_minutes(time_str)

        # Get all departures from this stop (they are sorted)
        departures = self._stop_times.get_stop_departures(stop_id, service, direction=direction, route_id=route_id)

        #self._sanity_check_departures(stop_id, departures)

        start_sec = target_sec - 30 * 60
        end_sec = target_sec + 30 * 60

        depart_count = 0
        for depart in departures:
            depart_sec = depart.get(KEY.DEPART_TIME)
            if depart_sec >= start_sec and depart_sec < end_sec:
                depart_count += 1
        return depart_count

    def get_departs_per_day(self, route, direction, stop_id, service):
        if isinstance(route, TransitRoute):
            route_id = route.get_id()
        else:
            route_id = route

        # Get all departures from this stop (they are sorted)
        departures = self._stop_times.get_stop_departures(stop_id, service, direction=direction, route_id=route_id)
        return len(departures)


    def _get_departs_per_hour_internal_OLD(self, route, stop_id, service, time_str, direction):
        """
        Attempting to get departures per hour based on interval between two departures
        is not working well. There are just too many screwey scenarios.  For example there
        are stops with departures on the same route/direction that leave a minute apart
        and then fork to different destination.  It might be simpler to just cound departures
        over a one hour interval
        """

        if isinstance(route, TransitRoute):
            route_id = route.get_id()
        else:
            route_id = route

        # Get target depart time
        target_sec = 60.0 * self._get_time_minutes(time_str)

        # Get all departures from this stop (they are sorted)
        departures = self._stop_times.get_stop_departures(stop_id, service, direction=direction, route_id=route_id)

        #self._sanity_check_departures(stop_id, departures)

        # Make a list with depart time as first item in tuple
        d = []
        for depart in departures:
            depart_sec = depart.get(KEY.DEPART_TIME)
            d.append((depart_sec, depart))

        first_after = None
        second_after = None
        first_before = None
        second_before = None
        seconds = None

        # Look for first occurance of time that is greater depart time while
        # keeping track of departures before and after
        for i, item in enumerate(d):

            second_before = first_before
            first_before = seconds

            seconds = item[0]

            if seconds < target_sec:
                try:
                    x = d[i+1]
                    first_after = x[0]
                except:
                    first_after = None

                try:
                    x = d[i+2]
                    second_after = x[0]
                except:
                    second_after = None
            else:
                break


        print "BEFORE: %s %s TIME: %s AFTER: %s %s" % \
              (repr(second_before), repr(first_before), repr(target_sec), repr(first_after), repr(second_after))

        interval = None

        if first_after is not None and first_before is not None:
            interval = first_after - first_before

            if first_after <= target_sec:
                self._dump_data(departures)

            if interval <= 0:
                self._dump_data(departures)

        elif first_before is not None:
            # Target time must be after last departure
            pass # No hourly departures for this scenarion.... its too late in the day
            # if second_before is not None:
            #     interval = first_before - second_before
            #     interval2 = target_sec - first_before
            #     if interval2 > interval:
            #         interval = None

        elif first_after is not None:
            # There are some departures after the target time (e.g, first thing in morning
            if second_after is not None:
                interval = second_after - first_after
                interval2 = first_after - target_sec
                # Only return hourly departures if the first departure is not too far away
                if interval2 > interval:
                    interval = None

            # depart_hour = depart_min / 60
            # leftover_min = depart_min - depart_hour * 60
            # print "depart time %d:%02d" % (depart_hour, leftover_min)
        departs_per_hour = 0

        if interval is not None:
            minutes = interval / 60

            if minutes == 0:
                for depart in departures:
                    print repr(depart)

            departs_per_hour = 60 / minutes

        # Sanity tests
        if departs_per_hour > 10:
            print "GOT %d departures (stop ID): %s" % (departs_per_hour, stop_id)
            self._dump_data(departures)

        return departs_per_hour

    def get_active_stops(self):

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
        result = [k for k in self._route_dict.iterkeys()]
        return result

    def get_routes(self):
        return [route for route in self._route_dict.itervalues()]
