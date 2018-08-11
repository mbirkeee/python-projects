import argparse
import my_utils
import pyproj
import random

from constants import BASE
from transit_routes import TransitRoutes
# from transit_shapes import TransitShapes
# from stop_times import TransitTrips

from plotter import Plotter
from plotter import ATTR

from geometry import Polyline
from geometry import Polypoint

from my_utils import base_path_from_date

class OverlayRunner():
    def __init__(self):

        self._base1 = BASE.JUNE
        self._base2 = BASE.JULY
        self._base3 = BASE.BRT

        plotter = Plotter()

        # self.plot_route(self._base1, plotter, 10125, "#0000ff", 6 )
        # self.plot_route(self._base2, plotter, 10232, "#ff0000", 4 )

        # self.plot_route(self._base3, plotter, 102281938, "#ff0000", 6 ) # red in
        # self.plot_route(self._base3, plotter, 102281939, "#ff0000", 6 ) # red out
        # self.plot_route(self._base3, plotter, 102281940, "#0000ff", 6 ) # blue in
        # self.plot_route(self._base3, plotter, 102281941, "#0000ff", 6 ) # blue out
        # self.plot_route(self._base3, plotter, 102281942, "#00ff00", 6 ) # green in
        # self.plot_route(self._base3, plotter, 102281943, "#00ff00", 6 ) # green out

        self.plot_route(self._base3, plotter, 102281966, "#0000ff", 6 ) # red in

        plotter.plot("temp/maps/route_overlay.html")

    def plot_route(self, base, plotter, route_id, color, thickness):

            routes = TransitRoutes(base, link_stops=False)

            polylines = routes.get_polylines(route_id)

            for polyline in polylines:
                print "Adding line", route_id, color
                polyline.set_attribute("strokeColor", color)
                polyline.set_attribute("strokeWeight", thickness)
                plotter.add_polyline(polyline)

            polydot = Polyline()
            polydot.set_attribute("radius", 400)

            stop_points = routes.get_stop_points(route_id)
            for point in stop_points:
                polydot.add_point(point)
            plotter.add_polypoint(polydot)

            polydot = Polyline()
            polydot.set_attribute("radius", 50)
            polydot.set_attribute("fillOpacity", 0.5)

            stop_points = routes.get_stop_points(route_id)
            for point in stop_points:
                polydot.add_point(point)
            plotter.add_polypoint(polydot)

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
        self._route_mgr = None

    def run(self):

        print self._route_id
        print self._base_path

        colorlist = [
            "#330000",
            "#660000"
            "#990000",
            "#003300",
            "#006600",
            "#009900",
            "#000033"
        ]

        result = []
        if self._route_id is None:
            self._route_mgr = TransitRoutes(self._base_path, link_shapes=True, link_stops=False)

            raise ValueError("plot all routes!!!")

            # routes = self._route_mgr.get_routes()
            # for route in routes:
            #     name = route.get_name()
            #     number = route.get_number()
            #     route_id = route.get_id()
            #     result.append((int(number), name, route_id))
            #
            # s = sorted(result)
            # for item in s:
            #     print "%5s  %60s %10s" % (repr(item[0]), item[1], repr(item[2]))
            #
            #     # Format for wiki table
            #     # print "|| %s || %s || %s || PDF || Map || Notes ||" % (repr(item[0]), item[1], repr(item[2]))

        else:
            self._route_mgr = TransitRoutes(self._base_path, link_shapes=True, link_stops=True)

            # Plot this route and it's s

            route = self._route_mgr.get_route(self._route_id)

            print "plot for route_id: %s - %d (%d)" % (route.get_name(), route.get_number(), self._route_id)

            plotter = Plotter()
            segments = route.get_segments()

            test_dict = {}
            if isinstance(segments, list):
                for i, segment in enumerate(segments):
                    test_dict[i] = segment
                segments = test_dict

            stops = route.get_stops()

            polypoint = Polyline()
            for stop in stops:
                polypoint.add_point(stop.get_point())

            polypoint.set_attribute(ATTR.RADIUS, 50)
            polypoint.set_attribute(ATTR.FILL_OPACITY, 0.8)
            polypoint.set_attribute(ATTR.FILL_COLOR, "#ff0000")

            plotter.add_polypoint(polypoint)

            for segment_id, segment in segments.iteritems():
                print "Plotting segment", segment_id
                color = "#0000ff"
                segment.set_attribute(ATTR.STROKE_COLOR, color)
                segment.set_attribute(ATTR.STROKE_WEIGHT, 2)
                plotter.add_polyline(segment)

            plotter.plot("temp/maps/route_%d.html" % int(self._route_id))

            for segment_id, segment in segments.iteritems():
                plotter = Plotter()
                color = "#0000ff"
                segment.set_attribute(ATTR.STROKE_COLOR, color)
                segment.set_attribute(ATTR.STROKE_WEIGHT, 2)
                plotter.add_polyline(segment)
                plotter.plot("temp/maps/segment_%d.html" % segment_id)

            # raise ValueError("DONE")
            #
            # trips = TransitTrips(self._base_path)
            # shapes = TransitShapes(self._base_path)
            #
            # # This just tests that all routes have shapes
            # route_ids = self._route_mgr.get_route_ids()
            # for test_route_id in route_ids:
            #     shape_ids = trips.get_shape_ids(test_route_id)
            #     points = shapes.get_points(shape_ids)
            #     if len(points) == 0:
            #         raise ValueError("fixme")
            #
            # shape_ids = trips.get_shape_ids(self._route_id)
            # points = shapes.get_points(shape_ids)
            #
            # plotter = Plotter()
            #
            # colorlist = [
            #     "#330000",
            #     "#660000"
            #     "#990000",
            #     "#003300",
            #     "#006600",
            #     "#009900",
            #     "#000033"
            # ]
            #
            # for i, shape_id in enumerate(shape_ids):
            #     polyline = Polyline()
            #     points = shapes.get_points(shape_id)
            #     for point in points:
            #         polyline.add_point(point)
            #
            #     color = colorlist[i]
            # #    color = "#%6x" % random.randint(0, 10000000)
            #     #color = "#0000ff"
            #     polyline.set_attribute("strokeColor", color)
            #     polyline.set_attribute("strokeWeight", i+2)
            #     plotter.add_polyline(polyline)
            #
            # plotter.plot("temp/maps/route_%d.html" % int(self._route_id))



if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Plop routes and stops per route')
   parser.add_argument("--route_id", help="Route ID", type=int)
   parser.add_argument("--date", help="june/july/brt", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()


#   runner = OverlayRunner()
