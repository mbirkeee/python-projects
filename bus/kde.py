import argparse
import my_utils
import pyproj

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE_RED_20, CIRCLE_RED_50

class Runner(object):

    def __init__(self, args):

        # self.user_id = args.user_id
        # self.start_time = args.start_time
        # self.stop_time = args.stop_time
        # self.shed = args.shed
        self._bandwidth = args.bandwidth
        self._myproj = pyproj.Proj("+init=EPSG:32613")
        self._transit = my_utils.TransitData()
        self._transit.load_stops()
        self._bus_stops = self._transit.get_data()

        print "Got bandwidth", self._bandwidth

    def plot_stops(self):

        print "Plotting %d points..." % len(self._bus_stops)

        map_name = "./data/maps/bus_stops.html"

        f = open(map_name, "w")
        f.write(MAP_TOP)
        f.write("var circle = {\n")

        i = 1
        for point in self._bus_stops.itervalues():
            lon = point.get('lon')
            lat = point.get('lat')
            f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))
            i+= 1

        f.write("};\n")
        f.write(CIRCLE_RED_50)
        f.write(MAP_BOTTOM)
        f.close()

        print "Wrote file: %s" % map_name

    def plot_grid_utm(self):

        steps_x = 100
        steps_y = 50

        min_point, max_point = self._transit.get_bounding_box_utm()
        print min_point
        print max_point

        border = 500.0

        min_x = min_point[0] - border
        max_x = max_point[0] + border

        min_y = min_point[1] - border
        max_y = max_point[1] + border

        step_size_x = (max_x - min_x) / steps_x
        step_size_y = (max_y - min_y) / steps_y

        map_name = "./data/maps/access_grid.html"

        f = open(map_name, "w")
        f.write(MAP_TOP)
        f.write("var circle = {\n")

        i = 0
        for x in xrange(steps_x + 1):
            for y in xrange(steps_y + 1):
                utm_x = min_x + x * step_size_x
                utm_y = min_y + y * step_size_y
                lon, lat = self._myproj(utm_x, utm_y, inverse=True)
                f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))
                i+= 1

        f.write("};\n")
        f.write(CIRCLE_RED_50)
        f.write(MAP_BOTTOM)
        f.close()

        print "Wrote file: %s" % map_name

    def plot_grid(self):

        steps_x = 100
        steps_y = 50

        min_point, max_point = self._transit.get_bounding_box()
        print min_point
        print max_point

        border = 0.0

        min_x = min_point[0] - border
        max_x = max_point[0] + border

        min_y = min_point[1] - border
        max_y = max_point[1] + border

        step_size_x = (max_x - min_x) / steps_x
        step_size_y = (max_y - min_y) / steps_y

        map_name = "./data/maps/access_grid.html"

        f = open(map_name, "w")
        f.write(MAP_TOP)
        f.write("var circle = {\n")

        i = 0
        for x in xrange(steps_x + 1):
            for y in xrange(steps_y + 1):
                lat = min_x + x * step_size_x
                lon = min_y + y * step_size_y
                # lon, lat = self._myproj(utm_x, utm_y, inverse=True)
                f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))
                i+= 1

        f.write("};\n")
        f.write(CIRCLE_RED_50)
        f.write(MAP_BOTTOM)
        f.close()

        print "Wrote file: %s" % map_name

    def test_bounding_box(self):
        min_l, max_l = self._transit.get_bounding_box()
        print min_l, max_l

        min_lat = min_l[0]
        min_lon = min_l[1]

        max_lat = max_l[0]
        max_lon = max_l[0]


        print self._myproj(min_lon, min_lat)
        print self._myproj(max_lon, max_lat)
        print self._myproj(min_lon, max_lat)
        print self._myproj(max_lon, min_lat)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Accessibility Heatmap')
    parser.add_argument("--bandwidth", help="KDE Bandwidth", type=float, required=True)
    # parser.add_argument("--start_time", help="Start Time", type=str, required=True)
    # parser.add_argument("--stop_time", help="Stop Time", type=str, required=True)
    # parser.add_argument("--shed", help="SHED", type=int, required=True)

    args = parser.parse_args()

    runner = Runner(args)
    # runner.plot_stops()
    runner.plot_grid()
    # runner.plot_grid_utm()
    #runner.test_bounding_box()