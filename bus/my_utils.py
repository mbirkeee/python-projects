import datetime
import time
import simplejson
import pyproj
import math

from geometry import Polygon
from geometry import Point

# from dataset import BASE

EXP_DECAY_PARAMS = {
    'exp_1' : {'c' : 25.504, 'x' : -.001 },
    'exp_2' : {'c' : 1.0, 'x' : -.001 },
}


PROJ = pyproj.Proj("+init=EPSG:32613")

def is_shapefile(base):
    if base.find('shapefile') >= 0:
        return True
    return False

# def base_path_from_date(date):
#     if date.find('jul') >= 0:
#         base = BASE.JULY
#     elif date.find('jun') >= 0:
#         base = BASE.JUNE
#     else:
#         base = BASE.BRT
#     return base

# Should be obsolete, points have distance method
# def get_point_dist(point1, point2):
#     if point1 is None or point2 is None: return 0.0
#
#     x1 = point1.get_x()
#     y1 = point1.get_y()
#
#     x2 = point2.get_x()
#     y2 = point2.get_y()
#
#     if x1 is None or x2 is None: return 0.0
#
#     return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2),2))

def get_dist(point1, point2):

    if point1 is None or point2 is None: return 0.0

    x1 = point1[0]
    y1 = point1[1]

    x2 = point2[0]
    y2 = point2[1]

    if x1 is None or x2 is None: return 0.0

    return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2),2))


def seconds_to_depart_time(seconds):
    minutes = seconds / 60
    hours = int(minutes / 60)
    remain = minutes - (60 * hours)
    return "%d:%02d" % (hours, remain)

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

class DaDwellingCounts(object):
    def __init__(self):
        self._data = {}
        self.load_file()

    def load_file(self):
        f = open('/Users/mikeb/Downloads/DA_dwelling_counts.csv')

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue

            try:
                print line.strip()
                parts = line.split(",")
                da_id = int(parts[0])
                dwelling_count = int(parts[1].strip())
                dwelling_size = float(parts[2].strip())

                print da_id, dwelling_count, dwelling_size

                if self._data.has_key(da_id):
                    raise ValueError("already have da_id")

                self._data[da_id] = (dwelling_count, dwelling_size)

            except Exception as err:
                print "failed to parse line"

        f.close()

    def get_for_da_id(self, da_id):
        return self._data.get(da_id)

class DaPopulations(object):
    def __init__(self):

        self._data_pop_by_da = {}
        self.load_stats_can_pop_data()

    def get_population_for_da_id(self, da_id):

        return int(self._data_pop_by_da[da_id])

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

class DaHeatmap(object):

    def __init__(self):
        self._data = {}
        self._max_score = 50

    def load_file(self, file_name):

        f = open(file_name, "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue
            # print line.strip()

            parts=line.split(",")
            da_id = int(parts[1].strip())
            score = float(parts[2].strip())

            try:
                # score = math.log10(score)
                score = score
            except Exception as err:
                print err
                score = 0

            if score > self._max_score:
                self._max_score = score

            # print da_id, score
            self._data[da_id] = score

        f.close()

        # print repr(self._data)

    def get_da_id_list(self):

        result = [k for k in self._data.iterkeys()]
        return result

    def get_score_normalized(self, da_id):
        score = self._data.get(da_id)
        normalized = score / self._max_score
        return normalized

    def get_score(self, da_id):
        return self._data.get(da_id)


def get_butterworth_decay(decay_method, point1, point2):

    parts = decay_method.split("_")
    distance_mode = parts[0].strip().lower()
    dpass = int(parts[1].strip())
    filter = Filter(dpass=dpass)
    distance = point1.get_distance(point2, method=distance_mode)
    decay = filter.run(distance)
    # print "-->>", distance_mode, dpass, distance, decay

    return decay

class Filter(object):

    def __init__(self, dpass=250, e=1, n=6):
        self._dpass = dpass
        self._e = e
        self._n = n

    def set_dpass(self, dpass):
        self._dpass = dpass

    def exp(self, distance):
        """
        This is an exponential decay as suggested by ehab
        """
        key = "exp_%d" % self._dpass
        param_dict = EXP_DECAY_PARAMS.get(key)
        c = param_dict.get('c')
        x = param_dict.get('x')

        result = c * math.pow(math.e, x * distance)
        return result

    def butterworth(self, distance):

        r = float(distance)/float(self._dpass)
        rp = math.pow(r, self._n)
        result = 1.0 / math.sqrt(1.0 + self._e * rp)
        return result

    def run(self, distance):
        return self.butterworth(distance)

class DaCentroidsOld(object):

    def __init__(self):
        self._data_pop_by_da = {}
        self._data_centriods = {}

        self._myproj = pyproj.Proj("+init=EPSG:32613")

        self.load_stats_can_pop_data()
        self.make_da_cvs_from_text()

    def load_stats_can_pop_data(self):

        f = open("data/2016_pop.csv", "r")

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

    def get_data(self, da_id):
        return self._data_centriods.get(da_id)


class TransitDataOBSOLETE(object):

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


