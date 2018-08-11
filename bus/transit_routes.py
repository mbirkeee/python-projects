import os
import shapefile

from geometry import Polyline
from geometry import Point

from route_id_names import ROUTE_IDS_05_04
from route_id_names import ROUTE_IDS_06_21
from route_id_names import BAD_STOP_IDS_BRT

from transit_trips import TransitTrips
from transit_shapes import TransitShapes

class TransitRoutesBrt(object):
    def __init__(self, base_path):
        self._base_path = base_path

        self._data = {}
        self._stop_dict = {}

        self._dir_dict = {
            "inbound"   : "IB",
            "outbound"  : "OB",
            "cw"        : "CW",
            "ccw"       : "CC"
        }

        self._active_stop_ids = None

        self.read_directions()
        self.read_stops()
        self.read_direction_stops()

    def get_stop_data(self, stop_id):
        return self._stop_dict.get(stop_id)

    def get_active_stop_ids(self):
        if self._active_stop_ids is None:
            result = []
            for stop_id, stop_data in self._stop_dict.iteritems():
                routes = stop_data.get('routes', [])
                if len(routes) > 0:
                    result.append(stop_id)
            self._active_stop_ids = result

        return self._active_stop_ids

    def get_polylines(self, route_id):
        """
        Return a list to be compatible with pre-brt data
        """
        p = Polyline()
        data = self._data.get(route_id)
        points = data.get('points')
        for point in points:
            # print point.get_lat_lng()
            p.add_point(point)

        print "BRT", route_id, p, len(p.get_points())
        return [p]

    def get_points(self, route_id):
        raise ValueError("fixme!!")

    def get_route_ids(self):
        result = [k for k in self._data.iterkeys()]
        return result

    def get_route_name(self, route_id):
        data = self._data.get(route_id, {})
        return data.get('name')

    def get_route_number(self, route_id):
        data = self._data.get(route_id, {})
        return data.get('number')

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
            number = int(name[:space_pos])
            name = name[space_pos:]

            d = record[2].strip().lower()

            direction = self._dir_dict.get(d)

            display_name = "%s (%s)" % (name.strip(), direction)
            route_id = int(record[1])

            if self._data.has_key(route_id):
                raise ValueError("Already have route key")

            points = [Point(p[1], p[0]) for p in shape.points]

            self._data[route_id] = {
                'name'      : display_name,
                "direction" : direction,
                "points"    : points,
                "number"    : number,
            }

    def read_direction_stops(self):

        """
        ['1424e21', 'HDR Future Network V3', '4174', 'Superstore',
        "10 Mainline, Confederation - Centre Mall (Inbound),
        14 Crosstown, St Paul's (Outbound),
        3 BRT, Green (Inbound),
        48 Suburban Connector, 33rd St - Confed (Inbound)"]
        """
        line_count = 0

        temp_dict = {}

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
                print "PARTS: %d" % len(parts)

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

                    dir_id = int(parts[part_index].strip())

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

                    stop_data = self._stop_dict.get(stop_id)
                    route_list = stop_data.get('routes', [])
                    route_list.append(dir_id)
                    route_list = list(set(route_list))
                    stop_data['routes'] = route_list

                    dist = parts[part_index + 2].strip()

                    # print "dir_id", dir_id, "stop_id", stop_id, "dist", dist, self.get_route_name(dir_id)
                    part_index += 3

                    stop_list = temp_dict.get(dir_id, [])
                    stop_list.append(stop_id)
                    temp_dict[dir_id] = stop_list

                # part_index = 0
                # for part in parts:
                #     print "part: %d: >>%s<<" % (part_index, part.strip())
                #     part_index += 1
                #     if part_index > 50:
                #         break

        f.close()

        for k, v in self._stop_dict.iteritems():
            print "Stop: %d routes: %d" % (k, len(v.get('routes', [])))

        for route_id, stop_list in temp_dict.iteritems():
            route_data = self._data.get(route_id)
            if route_data is None:
                # raise ValueError("failed to get route: %s" % route_id)
                print "failed to get route: %s" % route_id
                continue

            route_data['stops'] = stop_list
            # print stop_list

            self._data[route_id] = route_data

        x = [(route_id, route_data) for route_id, route_data in self._data.iteritems()]
        x = sorted(x)

        for item in x:
            route_data = item[1]
            print "Name: %s Stops: %d" % (route_data.get('name'), len(route_data.get('stops')))
        print "number of routes", len(x)

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

            stop_data = {
                'name' : stop_name,
                'point' : Point(float(lat), float(lng))
            }

            if bad_id is not None:
                stop_data['bad_id'] = bad_id

            # print "Adding", repr(stop_data)

            if self._stop_dict.has_key(stop_id):
                raise ValueError("already have stop id: %s %d" % (repr(stop_id), index))

            self._stop_dict[stop_id] = stop_data

        for k, v in self._stop_dict.iteritems():
            point = v.get('point')
            name = v.get('name')
            print "stop_id: %d name: %s lat:%f lng: %f" % (k, name, point.get_lat(), point.get_lng())

        print "Read %d stops" % len(self._stop_dict)


    def get_stop_points(self, route_id):

        result = []
        data = self._data.get(route_id)
        stops = data.get("stops")
        for stop_id in stops:
            stop_data = self._stop_dict.get(stop_id)
            if stop_data is None:
                print "ERROR: no data for stop", repr(stop_id)
                continue

            point = stop_data.get('point')
            result.append(point)
        return result

class TransitRoutes(object):

    def __init__(self, base_path):

        self._brt_mode = False

        if base_path.find("2018_05_04") > 0:
            print "this is the JUNE data"
            self._include_route_dict = ROUTE_IDS_05_04

        elif base_path.find('2018_08_05') > 0:
            print "this is the JULY data"
            self._include_route_dict = ROUTE_IDS_06_21

        else:
            self._brt_mode = True

        if self._brt_mode:
            self._brt = TransitRoutesBrt(base_path)
        else:
            self._base_path = base_path
            self._data = {}
            self._deprecated = {}
            self.read_file()
            self._transit_trips = None
            self._transit_shapes = None

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
                short_name = parts[4].strip()
                long_name = parts[5].strip()

                # I am not sure what the route type is
                route_type = int(parts[1].strip())

                if route_type != 3:
                    raise ValueError("route type not 3")

                print "read route ID", route_id

                if not self._include_route_dict.has_key(route_id):
                    print "SKIPPING ROUTE", route_id
                    self._deprecated[route_id] = (short_name, long_name)
                    continue


                if self._data.has_key(route_id):
                    raise ValueError("THIS IS A DUP!!!")

                self._data[route_id] = (short_name, long_name)

            print "number of routes:", len(self._data)
            print "%s: read %d lines" % (file_name, line_count)

        finally:
            if f:
                print "closing file"
                f.close()

        # ----- TEST -----
        route_id_list = self.get_route_ids()
        s = []
        for route_id in route_id_list:
            name = self.get_route_name_from_id(route_id)
            s.append((name, route_id))

        s = sorted(s)
        for i, item in enumerate(s):
            print "%d ID: %s NAME: %s" % (i+1, item[1], item[0])
        # ---- END TEST -----

    def get_stop_points(self, route_id):
        if self._brt_mode:
            return self._brt.get_stop_points(route_id)
        raise ValueError("fixme")

    def get_polylines(self, route_id):
        """
        Unfortunately the pre-BRT data routes are described in not one but several polylines.
        These MUST be plotted independently otherwise we get lots of spurious lines on the plot
        :param route_id:
        :return:
        """
        if self._brt_mode:
            return self._brt.get_polylines(route_id)

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
        if self._brt_mode:
            return self._brt.get_route_ids()

        result = [k for k in self._data.iterkeys()]
        return result

    def get_route_name_from_id(self, route_id):
        if self._brt_mode:
            return self._brt.get_route_name(route_id)

        data = self._data.get(route_id)
        if data is None:
            return "Unknown: %s" % repr(route_id)
        return data[1]

    def get_route_number_from_id(self, route_id):
        if self._brt_mode:
            return self._brt.get_route_number(route_id)

        data = self._data.get(route_id)
        if data is None:
            return "Unknown: %s" % repr(route_id)
        return data[0]


