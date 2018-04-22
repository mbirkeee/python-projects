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

        self.route_id = int(args.route_id)

        self.transitData = my_utils.TransitData()
        self._myproj = pyproj.Proj("+init=EPSG:32613")

    def run(self):

        self.transitData.load_stops()

        stop_data = self.transitData.get_stops()
        map_name = "./data/maps/bus_heatmap.html"

        f = open(map_name, "w")

        f.write(HEATMAP_TOP)
        f.write("function getPoints() {\nreturn [\n")

        for value in stop_data.itervalues():
            lon = value.get('lon')
            lat = value.get('lat')
            f.write("new google.maps.LatLng(%f, %f),\n" % (lat, lon))

        f.write("]\n")
        f.write(MAP_BOTTOM)

        f.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot Bus Route Heatmap Data')
    parser.add_argument("--route_id", help="Route ID", type=int, required=True)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()