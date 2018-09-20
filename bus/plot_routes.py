import argparse
import random

from data_manager import dataman_factory

from plotter import Plotter
from plotter import ATTR

from geometry import Polyline
from geometry import Polypoint


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

            routes = DataManager(base, link_stops=False)

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

        self._markers = args.markers
        self._all_markers = args.all_markers

        self._dataset = args.dataset
        self._dataman = None

    def all_stops_close(self, all_stops, route_stops, max_dist=1000):
        """
        Only include routes that are within max_dist of another stop on the route
        to reduce the number of markers shown on the map
        """

        result = []
        for potential_stop in all_stops:
            for route_stop in route_stops:
                d = potential_stop.get_distance(route_stop, method='crow')
                # print "distance", d
                if d < max_dist:
                    result.append(potential_stop)
                    break
        return result

    def plot_all_routes(self):
        """
        - plot all routes.
        """

        brt_routes = [
            102281938,
            102281939,
            102281940,
            102281941,
            102281942,
            102281943,
        ]

        plotter = Plotter()

        self._dataman = dataman_factory(self._dataset, link_route_shapes=True, link_stops=True)


        brt_stops = []
        total_stop_count = 0

        routes = self._dataman.get_routes()
        for route in routes:

            color = "#%6x" % random.randint(10000, 10000000)

            if route.get_id() in brt_routes:
                weight = 8
                brt_stops.extend(route.get_stops())
            else:
                weight = 4

            plotter.add_route(route, strokeColor=color, strokeWeight=weight, strokeOpacity=0.5)

            name = route.get_name()
            number = route.get_number()

            print "Route: %d %s" % (number, name)
            stops = route.get_stops()
            # print "Stops:", len(stops)
            total_stop_count += len(stops)

        # It makes sense that the total_stop_count is greater than the active stops, because
        # a stop may serve more than one route

        active_stops = self._dataman.get_active_stops()
        stops_existing = []
        stops_added = []
        for stop in active_stops:
            if stop.get_id() >= 30000:
                stops_added.append(stop)
            else:
                stops_existing.append(stop)

        plotter.add_stops(stops_existing, fillOpacity=0.5)

        if stops_added:
            plotter.add_stops(stops_added, fillColor="#0000ff", radius=60, fillOpacity=0.5)

        if brt_stops:
            brt_stops = list(set(brt_stops))
            plotter.add_stops(brt_stops, fillColor="#00ff00", radius=100, fillOpacity=0.5)

        print "Total Active Stop Count", total_stop_count, len(active_stops)
        print "Stops Existing:", len(stops_existing)
        print "Stops Added:", len(stops_added)
        print "Stops BRT:", len(brt_stops)

        if self._markers:
            for stop in active_stops:
                plotter.add_marker(stop.get_point(), stop.get_id(), stop.get_id())

        plotter.plot("temp/maps/all_routes_%s.html" % self._dataset)


        total_departures = 0
        for stop in active_stops:
            # print stop
            routes = stop.get_routes()
            for route in routes:
                # print route
                departures_0 = self._dataman.get_departs_per_week(route, 0, stop)
                departures_1 = self._dataman.get_departs_per_week(route, 0, stop)
                if departures_0 is not None:
                    total_departures += departures_0

                if departures_1 is not None:
                    total_departures += departures_1

        print "Total System Weekly Departures:", total_departures
        print "Departures per stop:", float(total_departures) / float(len(active_stops))

    def plot_one_route(self):

        self._dataman = dataman_factory(self._dataset, link_route_shapes=True, link_stops=True)

        # Plot this route and it's s

        route = self._dataman.get_route(self._route_id)

        print "plot for route_id: %s - %d (%d)" % (route.get_name(), route.get_number(), self._route_id)

        plotter = Plotter()
        segments = route.get_segments()

        test_dict = {}
        if isinstance(segments, list):
            for i, segment in enumerate(segments):
                test_dict[i] = segment
            segments = test_dict

        # Plot the stops for this route
        stops = route.get_stops()
        plotter.add_stops(stops, fillOpacity=0.2)
        plotter.add_stops(stops, radius=650.0/2.0, fillOpacity=0.1)

        added_stops = route.get_stops_added()
        plotter.add_stops(added_stops, radius=30, fillColor="#0000ff", fillOpacity=0.3)

        removed_stops = route.get_stops_removed()
        plotter.add_stops(removed_stops, radius=25, fillColor="#808080", fillOpacity=0.4)

        if self._all_markers:
            self._markers = True
            stops = self.all_stops_close(self._dataman.get_stops(), stops)

        if self._markers:
            for stop in stops:
                msg = "LAT: %f LNG: %f" % (stop.get_lat(), stop.get_lng())
                plotter.add_marker(stop.get_point(), stop.get_id(), msg)

        plotter.add_route(route)

        plotter.plot("temp/maps/dataset_%s_route_%d.html" % (self._dataset, int(self._route_id)))

        print "Route: %d (%d - %s) has %d stops" % \
              (route.get_id(), route.get_number(), route.get_name(), len(route.get_stops()))

        # for segment_id, segment in segments.iteritems():
        #     plotter = Plotter()
        #     color = "#0000ff"
        #     segment.set_attribute(ATTR.STROKE_COLOR, color)
        #     segment.set_attribute(ATTR.STROKE_WEIGHT, 2)
        #     plotter.add_polyline(segment)
        #     plotter.plot("temp/maps/segment_%d.html" % segment_id)

    def run(self):


        result = []
        if self._route_id is None:




            self.plot_all_routes()
        else:
            self.plot_one_route()
if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Plot routes and stops per route')
   parser.add_argument("-r", "--route_id", help="Route ID", type=int)
   parser.add_argument("-d", "--dataset", help="june/july/brt/brt1", type=str, required=True)
   parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
   parser.add_argument("-a", "--all_markers", help="Include ALL stop markers", required=False, action='store_true')

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()


#   runner = OverlayRunner()
