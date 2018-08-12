import argparse
from transit_routes import TransitRoutes


from plotter import Plotter
from plotter import ATTR

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
            self._stop_id = None

        self._date = args.date
        self._base_path = base_path_from_date(args.date)

        self._route_mgr = TransitRoutes(self._base_path, link_stops=True, link_shapes=True)

    def run(self):

        if self._stop_id is None:
            plotter = Plotter()
            polypoint = Polyline()

            routes = self._route_mgr.get_routes()
            for route in routes:
                segments = route.get_segments()

                for segment in segments:
                    segment.set_attribute(ATTR.STROKE_COLOR, "#0000ff")
                    segment.set_attribute(ATTR.STROKE_WEIGHT, 3)
                    segment.set_attribute(ATTR.STROKE_OPACITY, 0.8)
                    plotter.add_polyline(segment)

            stops = self._route_mgr.get_active_stops()

            for stop in stops:
                 polypoint.add_point(stop.get_point())

            polypoint.set_attribute(ATTR.FILL_OPACITY, 0.8)
            polypoint.set_attribute(ATTR.RADIUS, 90)
            plotter.add_polypoint(polypoint)

            print "Active stops:", len(stops)

            plotter.plot("temp/maps/stop_locations_%s.html" % self._date)
        else:
            print " one stop id?"


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Plot all stops')
   parser.add_argument("--stop_id", help="Stop ID", type=int)
   parser.add_argument("--date", help="june/july/brt", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()

