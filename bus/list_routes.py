import argparse
import my_utils
import pyproj
import random

from transit_routes import TransitRoutes
from transit_shapes import TransitShapes
from stop_times import TransitTrips

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2
from heatmap_html import HEATMAP_TOP

from plotter import Plotter
from geometry import Polyline

from my_utils import base_path_from_date


class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        try:
            self._route_id = int(args.route_id)
        except:
            self._route_id = None

        self._date = args.date
        self._base_path = base_path_from_date(args.date)

        self._routes = TransitRoutes(self._base_path)

    def run(self):

        print self._route_id
        print self._base_path

        result = []
        if self._route_id is None:
            route_ids = self._routes.get_route_ids()
            for route_id in route_ids:
                name = self._routes.get_route_name_from_id(route_id)
                number = self._routes.get_route_number_from_id(route_id)

                result.append((int(number), name, route_id))

            s = sorted(result)
            for item in s:
                print "%5s  %60s %10s" % (repr(item[0]), item[1], repr(item[2]))

                # Format for wiki table
                # print "|| %s || %s || %s || PDF || Map || Notes ||" % (repr(item[0]), item[1], repr(item[2]))

        else:
            print "plot for route_id: %d" % self._route_id
            # Plot this route and it's stops
            trips = TransitTrips(self._base_path)
            shapes = TransitShapes(self._base_path)

            # This just tests that all routes have shapes
            route_ids = self._routes.get_route_ids()
            for test_route_id in route_ids:
                shape_ids = trips.get_shape_ids(test_route_id)
                points = shapes.get_points(shape_ids)
                if len(points) == 0:
                    raise ValueError("fixme")

            shape_ids = trips.get_shape_ids(self._route_id)
            points = shapes.get_points(shape_ids)

            plotter = Plotter()

            colorlist = [
                "#330000",
                "#660000"
                "#990000",
                "#003300",
                "#006600",
                "#009900",
                "#000033"
            ]

            for i, shape_id in enumerate(shape_ids):
                polyline = Polyline()
                points = shapes.get_points(shape_id)
                for point in points:
                    polyline.add_point(point)

                color = colorlist[i]
            #    color = "#%6x" % random.randint(0, 10000000)
                #color = "#0000ff"
                polyline.add_attribute("strokeColor", color)
                polyline.add_attribute("strokeWeight", i+2)
                plotter.add_polyline(polyline)

            plotter.plot("temp/maps/route_%d.html" % int(self._route_id))

if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='List routes and stops per route')
   parser.add_argument("--route_id", help="Route ID", type=int)
   parser.add_argument("--date", help="june/july/brt", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()
