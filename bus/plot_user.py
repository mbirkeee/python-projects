import argparse
import my_utils
import pyproj

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2
from heatmap_html import HEATMAP_TOP

class Runner(object):
    """
    This program plots GPS data for one user
    """
    def __init__(self, args):

        self.user_id = int(args.user_id)
        self.start_time = args.start_time
        self.stop_time = args.stop_time
        self.shed = int(args.shed)
        self.heatmap = args.heatmap

        self._myproj = pyproj.Proj("+init=EPSG:32613")

    def run(self):

        print "heatmap", self.heatmap

        start_sec = my_utils.string_to_seconds(self.start_time)
        stop_sec =  my_utils.string_to_seconds(self.stop_time)

        user_data = my_utils.UserGPS(self.shed, self.user_id)
        user_points = user_data.load(start_sec=start_sec, stop_sec=stop_sec)

        min_time = user_data.get_min_time()
        print "User earliest time: %s" % my_utils.seconds_to_string(min_time)

        max_time = user_data.get_max_time()
        print "User latest time:   %s" % my_utils.seconds_to_string(max_time)

        if len(user_points) == 0:
            print "Nothing to plot... returning"
            return

        print "Plotting %d points..." % len(user_points)

        map_name = "./data/maps/user_%d_shed_%d.html" % (int(self.user_id), self.shed)

        f = open(map_name, "w")


        if self.heatmap:
            f.write(HEATMAP_TOP)

            f.write("function getPoints() {\nreturn [\n")

            for i, point in enumerate(user_points):
                lon, lat = self._myproj(point[0], point[1], inverse=True)
                f.write("new google.maps.LatLng(%f, %f),\n" % (lat, lon))

            f.write("]\n")
            f.write(MAP_BOTTOM)

        else:

            f.write(MAP_TOP)
            f.write("var circle2 = {\n")
            for i, point in enumerate(user_points):

                lon, lat = self._myproj(point[0], point[1], inverse=True)
                f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))


            f.write("};\n")
            f.write(CIRCLE2)
            f.write(MAP_BOTTOM)

        f.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot data for one user')
    parser.add_argument("--user_id", help="User ID", type=int, required=True)
    parser.add_argument("--start_time", help="Start Time", type=str)
    parser.add_argument("--stop_time", help="Stop Time", type=str)
    parser.add_argument("--shed", help="SHED", type=int, required=True)
    parser.add_argument("--heatmap", help="heatmap", action="store_true")

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()