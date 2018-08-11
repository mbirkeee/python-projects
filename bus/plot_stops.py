import argparse
import my_utils
import pyproj
import random

from constants import BASE
from transit_routes import TransitRoutes
from transit_shapes import TransitShapes
from transit_stops import TransitStops
from stop_times import TransitTrips

from plotter import Plotter
from geometry import Polyline

from my_utils import base_path_from_date


class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        try:
            self._stop_id = int(args.stop_id)
        except:
            self._route_id = None

        self._date = args.date
        self._base_path = base_path_from_date(args.date)

        self._stop_mgr = TransitStops(self._base_path)


        raise ValueError("temp stop")

    def run(self):

        print self._stop_id

        plotter = Plotter()
        polypoint = Polyline()

        stops = self._stop_mgr.get_stops()

        for stop_id in stop_ids:
            print "Adding location for", stop_id
            point = stop.get_point(stop_id)
            print point
            polypoint.add_point(stop.get_point(stop_id))
        polypoint.set_attribute("fillOpacity", 0.8)
        polypoint.set_attribute("radius", 50)
        plotter.add_polypoint(polypoint)
        plotter.plot("temp/maps/stop_locations.html")



if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Plot all stops')
   parser.add_argument("--stop_id", help="Stop ID", type=int)
   parser.add_argument("--date", help="june/july/brt", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()

