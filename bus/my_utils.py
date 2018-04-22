import datetime
import time
import simplejson

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


class TransitData(object):

    def __init__(self):
        self._bus_stops = None

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
