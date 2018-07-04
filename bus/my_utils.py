import datetime
import time
import simplejson
import pyproj
import math

def get_dist(point1, point2):

    if point1 is None or point2 is None: return 0.0

    x1 = point1[0]
    y1 = point1[1]

    x2 = point2[0]
    y2 = point2[1]

    if x1 is None or x2 is None: return 0.0

    return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2),2))

def seconds_to_string(seconds):
    t = datetime.datetime.fromtimestamp(seconds)
    tt = t.strftime("%Y-%m-%d:%H:%M:%S")
    return tt

def string_to_seconds(s):

    if s is None:
        return

    try:
        t = time.strptime(s.strip(), "%Y-%m-%d:%H:%M:%S")
        return int(time.mktime(t))
    except:
        pass

    try:
        t = time.strptime(s.strip(), "%Y-%m-%d:%H:%M")
        return int(time.mktime(t))
    except:
        pass

    try:
        t = time.strptime(s.strip(), "%Y-%m-%d:%H")
        return int(time.mktime(t))
    except:
        pass

    try:
        t = time.strptime(s.strip(), "%Y-%m-%d")
        return int(time.mktime(t))
    except:
        pass

    try:
        t = time.strptime(s.strip(), "%Y-%m")
        return int(time.mktime(t))
    except:
        pass

    try:
        t = time.strptime(s.strip(), "%Y")
        return int(time.mktime(t))
    except:
        pass

    raise ValueError("Invalid time string: %s" % s)


class DaCentriods(object):

    def __init__(self):
        self._data_pop_by_da = {}
        self._data_centriods = {}

        self._myproj = pyproj.Proj("+init=EPSG:32613")

        self.load_stats_can_pop_data()
        self.make_da_cvs_from_text()

    def load_stats_can_pop_data(self):

        f = open("../data/2016_pop.csv", "r")

        expected_parts = 15

        for line in f:
            # print "LINE", line.strip()
            parts = line.split(",")
            # print len(parts)

            if len(parts) != expected_parts:
                print "BAD LINE!!!!!", line
                print len(parts)
                continue

            try:
                da_id = int(parts[1].strip('"'))
                pop = int(parts[12].strip('"'))
            except Exception as err:
                print "Failed for line:", line
                continue
                # raise ValueError("unexpected number of parts")

            print "DA ID:", da_id, "POP:", pop

            if self._data_pop_by_da.has_key(da_id):
                raise ValueError("Already have da_id: %s" % da_id)

            self._data_pop_by_da[da_id] = pop

        f.close()

    def make_da_cvs_from_text(self):

        # I think that DA_centriods.txt is a file produced by ArcGIS
        f = open("../data/DA_centriods.txt", 'r')
        count = 0

        for line in f:
            count += 1
            if count == 1: continue

            parts = line.strip().split(",")
            # print parts

            try:
                da_id = int(parts[1].strip())
                da_fid = int(parts[23].strip())
                lat = float(parts[24].strip())
                lon = float(parts[25].strip())
            except:
                print "BAD LINE", line
                continue

            # print da_id, da_fid, lat, lon

            population = self._data_pop_by_da.get(da_id)
            if population is None:
                raise ValueError("Failed to get pop for %s" % repr(da_id))

            x, y  = self._myproj(lon, lat)

            self._data_centriods[da_id] = {
                'x'         : x,
                'y'         : y,
                'lat'       : lat,
                'lon'       : lon,
                'da_fid'    : da_fid,
                'pop'       : population
            }

        f.close()

    def get_list(self):
        result = [k for k in self._data_centriods.iterkeys()]
        return result

    def get_centriods(self):
        return self._data_centriods

    def get_population(self, da_id):

        if not self._data_centriods.has_key(da_id):
            return None

        data = self._data_centriods.get(da_id)
        return data.get('pop')

    def get_utm(self, da_id):

        if not self._data_centriods.has_key(da_id):
            return None

        data = self._data_centriods.get(da_id)
        return (data.get('x'), data.get('y'))


class TransitData(object):

    def __init__(self):
        self._bus_stops = None
        self._myproj = pyproj.Proj("+init=EPSG:32613")

    def load_route(self, route_id):
        f = open('data/transit/bus_routes.json', 'r')
        bus_routes = simplejson.load(f)
        f.close()

        # for route_id in bus_routes.iterkeys():
        #     print "route_id", route_id, type(route_id)

        route_data = bus_routes.get(str(route_id))
        return route_data

    def load_stops(self):
        file_name = './data/transit/bus_stops.json'
        f = open(file_name, 'r')
        self._bus_stops = simplejson.load(f)
        f.close()


    def load_stops_from_csv(self, file_name):
        """
        0 stop_id,
        1 stop_code,
        2 stop_lat,
        3 stop_lon,
        4 location_type,
        5 wheelchair_boarding,
        6 name
        """
        result = {}

        line_count = 0
        f = open(file_name)

        for line in f:
            line_count += 1
            if line_count == 1: continue

            try:
                parts = line.split(",")
                stop_code = int(parts[1].strip())
                name = parts[6].strip()
                lat = float(parts[2].strip())
                lon = float(parts[3].strip())

                print stop_code, lat, lon, name

                x, y  = self._myproj(lon, lat)
                stop_data = {
                    'lat'   : lat,
                    'lon'   : lon,
                    'x'     : x,
                    'y'     : y,
                    'name'  : name
                }

                result[stop_code] = stop_data

            except Exception as err:
                print "Exception processing line: %s" % repr(err)
                print "line: %s" % line


        f.close()

        self._bus_stops = result

    def get_stop_id_list(self):
        result = [k for k in self._bus_stops.iterkeys()]
        return result

    def get_stop_utm(self, stop_id):
        stop_data = self._bus_stops.get(stop_id)
        if stop_data is None:
            return None
        return (stop_data.get('x'), stop_data.get('y'))

    def get_stop_name(self, stop_id):
        stop_data = self._bus_stops.get(stop_id)
        if stop_data is None:
            return None
        return stop_data.get('name')

    def get_stops(self):
        return self._bus_stops

    def get_data(self):
        raise ValueError("fix me obsolete")
        return self._bus_stops

    def get_bounding_box(self):

        min_lat =  9999999999.0
        min_lon =  9999999999.0
        max_lat = -9999999999.0
        max_lon = -9999999999.0

        for key, value in self._bus_stops.iteritems():

            lat = value.get('lat')
            lon = value.get('lon')

            if lat < min_lat:
                min_lat = lat

            if lat > max_lat:
                max_lat = lat

            if lon < min_lon:
                min_lon = lon

            if lon > max_lon:
                max_lon = lon

        return (min_lat, min_lon), (max_lat, max_lon)

    def get_bounding_box_utm(self):

        min_x =  9999999999.0
        min_y =  9999999999.0
        max_x = -9999999999.0
        max_y = -9999999999.0

        for key, value in self._bus_stops.iteritems():

            x = value.get('x')
            y = value.get('y')

            if x < min_x:
                min_x = x

            if x > max_x:
                max_x = x

            if y < min_y:
                min_y = y

            if y > max_y:
                max_y = y

        return (min_x, min_y), (max_x, max_y)

class UserGPS(object):

    def __init__(self, shed, user_id):

        self._shed = shed
        self._user_id = user_id

        self._result = []

        self._min_time = None
        self._max_time = None

    def load(self, start_sec=None, stop_sec=None):

        result = []

        file_name = "./data/shed%d/user_gps/user_gps_%s.csv" % (self._shed, self._user_id)
        line_count = 0

        f = open(file_name, "r")

        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            x = float(parts[0].strip())
            y = float(parts[1].strip())
            seconds = int(parts[2].strip())

            if self._min_time is None or seconds < self._min_time:
                self._min_time = seconds

            if self._max_time is None or seconds > self._max_time:
                self._max_time = seconds

            if start_sec and seconds < start_sec:
                continue

            if stop_sec and seconds > stop_sec:
                continue

            self._result.append((x, y, seconds))

        print "Earliest time:", seconds_to_string(self._min_time)
        print "Latest time:", seconds_to_string(self._max_time)
        print "Total points:", len(self._result)
        print "Loaded %s" % file_name

        return self._result


    def get_max_time(self):
        return self._max_time

    def get_min_time(self):
        return self._min_time
