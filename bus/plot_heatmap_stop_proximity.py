import argparse
import my_utils
import pyproj
import random

from constants import BASE
from da_manager import DaData
from transit_routes import TransitRoutes
# from transit_shapes import TransitShapes
# from stop_times import TransitTrips

from plotter import Plotter
from plotter import ATTR

from geometry import Polyline
from geometry import Polypoint

from my_utils import base_path_from_date

class Runner(object):
    """
    This program generates and plots a heatmap for proximity to stops
    """
    def __init__(self, args):

        try:
            self._plot_route_ids = [int(args.route_id)]
        except:
            self._plot_route_ids = []

        self._date = args.date
        self._base_path = base_path_from_date(args.date)
        self._dataman = TransitRoutes(self._base_path)

    def run(self):

        das = DaData()

        group1 = das.get_polygons()

        print "Plotting Proximity heatmap --------------------------------------"

        # Make a list of all routes to plot
        plot_routes = []
        routes = self._dataman.get_routes()
        for route in routes:
            consider = False
            if not self._plot_route_ids:
                consider  = True
            else:
                if route.get_id() in self._plot_route_ids:
                    consider = True
            if consider:
                plot_routes.append(route)
                print "PROCESSING ROUTE", route.get_id(), route.get_name()
            else:
                print "SKIPPING ROUTE", route.get_id(), route.get_name()

        # Make a list of stops to consider
        stop_ids = []
        for route in plot_routes:
            stop_ids.extend(route.get_stop_ids())

        print "Stop list len", len(stop_ids)
        stop_ids = list(set(stop_ids))
        print "Stop list len (no duplicates)", len(stop_ids)

        plotter = Plotter()

        # Add DAs to the plot
        plotter.add_das(das)

        plotter.plot("temp/maps/stop_proximity_%s.html" % self._date)

if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Heatmap - Proximity to stops')
   parser.add_argument("--route_id", help="Route ID", type=int)
   parser.add_argument("--date", help="june/july/brt", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()

