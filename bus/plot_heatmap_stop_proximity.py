import argparse
import my_utils
import pyproj
import random

from constants import BASE
from da_manager import DaData
from transit_routes import TransitRoutes
# from transit_shapes import TransitShapes
# from stop_times import TransitTrips
from intersect import Intersect
from my_utils import Filter

from plotter import Plotter
from plotter import ATTR

from geometry import Polyline
from geometry import Polypoint

from shapefile_writer import ShapeFileWriter
from score import Score

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

        da_mgr = DaData()
        das = da_mgr.get_das()

        if False:
            da_id_list = [
                47110049,
                47110045,
                47110046,
            ]

            das = []
            for da_id in da_id_list:
                das.append(da_mgr.get_da(da_id))


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

        filter = Filter()

        stops = []
        for stop_id in stop_ids:
            stop = self._dataman.get_stop(stop_id)
            stop.make_round_buffer(400)
            stops.append(stop)

        # Even though logically I would like to perform the intersection in the
        # call to compute demand, it is more efficient to do it here because the
        # results are used again later on

        intersect = Intersect(stops, das)
        # for stop in stops:
        #     stop.compute_demand(intersect, filter)

        plotter = Plotter()

        shapefile = ShapeFileWriter()

        judge = Score()

        plot_rasters = []
        for da in das:
            rasters = da.get_rasters(100)
            for raster in rasters:
                stop_tuples = intersect.get_intersections(group=2, id=da.get_id())
                score = judge.get_score_simple(raster, stop_tuples)
                if score > 0:
                    plot_rasters.append((score, raster))

                # plotter.add_polygon(raster.get_polygon())
        # Add DAs to the plot
        max_score = 0
        for item in plot_rasters:
            if item[0] > max_score:
                max_score = item[0]

        for item in plot_rasters:
            score = item[0]
            raster = item[1]
            print "Raster ID", raster.get_id()
            print "Raster Parent", raster.get_parent_id()

            shapefile.add_raster(raster, score)

            p = raster.get_polygon()
            opacity = score / max_score
            p.set_attribute(ATTR.FILL_OPACITY, opacity)
            p.set_attribute(ATTR.STROKE_WEIGHT, 0)
            p.set_attribute(ATTR.STROKE_COLOR, "#202020")
            p.set_attribute(ATTR.STROKE_OPACITY, 0)
            plotter.add_polygon(p)


        plotter.add_das(da_mgr.get_das())

        plotter.plot("temp/maps/stop_proximity_%s.html" % self._date)
        shapefile.write("temp/shapefiles/stop_proximity_%s.shp" % self._date)

if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Heatmap - Proximity to stops')
   parser.add_argument("--route_id", help="Route ID", type=int)
   parser.add_argument("--date", help="june/july/brt", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()

