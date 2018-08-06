import datetime
import time
import simplejson
import pyproj
import math

from geometry import Polygon
from geometry import Point

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import POLYGON
from map_html import MARKER
from map_html import CIRCLE_RED_20
from map_html import CIRCLE_RED_5

PROJ = pyproj.Proj("+init=EPSG:32613")

def get_point_dist(point1, point2):
    if point1 is None or point2 is None: return 0.0

    x1 = point1.get_x()
    y1 = point1.get_y()

    x2 = point2.get_x()
    y2 = point2.get_y()

    if x1 is None or x2 is None: return 0.0

    return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2),2))

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


class DaData(object):

    def __init__(self):

        self._data = {}
        self._polygons = {}

        self.load_file("data/DA_polygon_points.csv")
        self.load_file_centroids("data/DA_centroids.csv")

        # This data can be used to clip DA polygons to get a much more realistic
        # approximation of the populated areas
        self._clip_points = {
            # This is the westside DA... e.g. near blairmore walmart
            47110581 : [
                (52.119256, -106.765271),
                (52.141280, -106.765271),
                (52.141280, -106.751404),
                (52.119256, -106.751404)
            ],
            47110694 : [
                (52.115015, -106.745332),
                (52.104551, -106.745332),
                (52.104551, -106.715892),
                (52.115015, -106.715892)
            ],
            47110540 : [
                (52.115085, -106.699720),
                (52.106229, -106.699720),
                (52.106229, -106.680867),
                (52.115085, -106.680867),
            ],
            47110699 : [
                (52.096483, -106.662102),
                (52.070744, -106.662102),
                (52.070744, -106.645623),
                (52.096483, -106.645623)
            ],
            47110524 : [
                (52.107555, -106.579190),
                (52.083615, -106.579190),
                (52.083615, -106.543656),
                (52.107555, -106.543656)
            ],
            47110689 : [
                (52.140231, -106.561423),
                (52.120732, -106.561423),
                (52.120732, -106.539879),
                (52.140231, -106.539879)
            ],
            47110664 : [
                (52.174050, -106.585627),
                (52.157045, -106.585627),
                (52.157045, -106.548548),
                (52.174050, -106.548548)
            ],
            # North Industrial Area
            47110691 : [
                (52.180000, -106.691798),
                (52.140824, -106.691798),
                (52.140824, -106.620598),
                (52.180000, -106.620598)
            ],
            # Airport
            47110397 : [
                (52.169926, -106.691456),
                (52.156342, -106.691456),
                (52.156342, -106.666565),
                (52.169926, -106.666565)
            ],
            # Lakeview
            47110147 : [
                (52.096588, -106.605754),
                (52.088705, -106.605754),
                (52.088705, -106.586013),
                (52.096588, -106.586013)
            ]
        }
        self._clipping_polygons = {}
        self._clipped_polygons = {}
        self._make_clipping_polygons()
        self._clip()

        self._use_clipped_area()

    def _use_clipped_area(self):
        for da_id, p in self._clipped_polygons.iteritems():
            da_p = self.get_polygon(da_id)
            old_area = da_p.get_area()
            da_p.set_area(p.get_area())
            new_area = da_p.get_area()
            f = new_area/old_area
            print "DA %d aread %.2f ---> %.2f (%.2f)" % (da_id, old_area, new_area, f)

    def _clip(self):

        for da_id, clipping_p in self._clipping_polygons.iteritems():

            da_p = self.get_polygon(da_id)

            intersection = da_p.intersect(clipping_p)
            if len(intersection) != 1:
                raise ValueError('fixme!!')
            self._clipped_polygons[da_id] = intersection[0]

    def _make_clipping_polygons(self):

        for da_id, points in self._clip_points.iteritems():
            p = Polygon()
            for point in points:
                p.add_point(Point(point[0], point[1]))
            self._clipping_polygons[da_id] = p

    def get_clipping_polygons(self):

        result = []
        for da_id, p in self._clipping_polygons.iteritems():
            result.append(p)
        return result

    def get_clipped_polygons(self):

        result = []
        for da_id, p in self._clipped_polygons.iteritems():
            result.append(p)
        return result

    def load_file(self, file_name):

        f = open(file_name, "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue
            # print line.strip()

            parts=line.split(",")
            da_id = int(parts[0].strip())
            point_index = int(parts[1].strip())
            lat = float(parts[2].strip())
            lng = float(parts[3].strip())

            # print da_id, point_index, lat, lng

            point = Point(lat, lng)

            data = self._data.get(da_id, {})
            data[point_index] = point
            self._data[da_id] = data

        f.close()
        print "loaded %d points from %s" % (count, file_name)

    def get_area(self, da_id):
        polygon = self.get_polygon(da_id)
        return polygon.get_area()

    def get_da_id_list(self):
        result = [k for k in self._data.iterkeys()]
        return result

    def get_polygons(self):

        result = {}
        for da_id in self._data.iterkeys():
            result[da_id] = self.get_polygon(da_id)
        return result

    def get_polygon(self, da_id):

        polygon = self._polygons.get(da_id)

        if polygon is None:
            points_dict = self._data.get(da_id)
            polygon = Polygon()

            point_index = 0
            while True:
                point = points_dict.get(point_index)
                if point is None: break
                polygon.add_point(point)
                point_index += 1
            self._polygons[da_id] = polygon

        return polygon

    def get_population(self, da_id):
        data = self._data.get(da_id)
        return data.get('pop')

    def get_centroid(self, da_id):
        polygon = self._polygons.get(da_id)
        return polygon.get_centroid()

        # data = self._data.get(da_id)
        # if data is None:
        #     raise ValueError("No data for da_id: %s" % repr(da_id))
        # return data.get('centroid')

    def load_file_centroids(self, file_name):

        f = open(file_name, "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue

            parts=line.split(",")
            da_id = int(parts[1].strip())
            lat = float(parts[2].strip())
            lng = float(parts[3].strip())
            pop = int(parts[4].strip())

            centroid = Point(lat, lng)

            data = self._data.get(da_id, {})

            # data['centroid'] = centroid
            data['pop'] = pop
            self._data[da_id] = data

        f.close()

        print "loaded %d centroids from %s" % (count, file_name)

class Weight(object):

    def __init__(self):
        # self._dpass = 250
        self._dpass = 150
        self._e = 1
        self._n = 6

    def butterworth(self, distance):

        r = float(distance)/float(self._dpass)
        rp = math.pow(r, self._n)
        result = 1.0 / math.sqrt(1.0 + self._e * rp)
        return result

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





class PlotPolygons(object):

    def __init__(self):
        print "polygon plotter instantiated"

        self._polygon_list = []
        self._marker_list = []
        self._dot_list = []

    def add_dot(self, point):
        self._dot_list.append(point)

    def add_marker(self, point, title, label):
        self._marker_list.append((point, title, label))

    def add_polygon(self, items):

        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not isinstance(item, Polygon):
                raise ValueError("not a Polygon")
            #print "ADD item", item
            self._polygon_list.append(item)

    def plot(self, file_name):
        print "plot called", file_name

        f = open(file_name, "w")
        f.write(MAP_TOP)

        for item in self._polygon_list:
            f.write("var polypoints = [\n")
            points = item.get_points()

            for point in points:
                f.write("{lat: %f, lng: %f},\n" % point.get_lat_lng())
            f.write("];\n")

            # fill_opacity = float(random.randint(0, 1000)/1000.0)

            stroke_color = item.get_attribute("strokeColor", default="#202020")
            stroke_opacity = item.get_attribute("strokeOpacity", default=0.5)
            stroke_weight = item.get_attribute("strokeWeight", default=1)
            fill_color = item.get_attribute("fillColor", default="#ff0000")
            fill_opacity = item.get_attribute("fillOpacity", default=0.1)

            f.write(POLYGON % (stroke_color, stroke_opacity, stroke_weight, fill_color, fill_opacity))

        if len(self._marker_list) > 0:

            f.write("var marker = {\n")
            i = 0
            for item in self._marker_list:
                point = item[0]
                title = item[1]
                label = item[2]
                lat = point.get_lat()
                lng = point.get_lng()
                f.write("%d:{center:{lat:%f,lng:%f},title:'%s',label:'%s',},\n" % (i, lat, lng, title, label))
                i += 1

            f.write("};\n")
            f.write(MARKER)

        if len(self._dot_list) > 0:

            f.write("var circle = {\n")
            i = 0
            for item in self._dot_list:
                point = item
                lat = point.get_lat()
                lng = point.get_lng()
                f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lng))
                i += 1

            f.write("};\n")
            f.write(CIRCLE_RED_5)

        f.write(MAP_BOTTOM)
        f.close()
        print "Wrote MAP file: %s" %file_name
