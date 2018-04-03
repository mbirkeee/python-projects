import argparse
import my_utils
import pyproj

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2

class Runner(object):

    def __init__(self, args):

        self.user_id = args.user_id
        self.start_time = args.start_time
        self.stop_time = args.stop_time
        self.shed = args.shed
        self._myproj = pyproj.Proj("+init=EPSG:32613")

    def run(self):

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

        map_name = "./data/maps/user_points.html"

        f = open(map_name, "w")
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
    parser.add_argument("--start_time", help="Start Time", type=str, required=True)
    parser.add_argument("--stop_time", help="Stop Time", type=str, required=True)
    parser.add_argument("--shed", help="SHED", type=int, required=True)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()