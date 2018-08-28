import argparse

from my_utils import seconds_to_string
from my_utils import seconds_to_depart_time
from data_manager import dataman_factory
from plotter import Plotter
from plotter import ATTR
from geometry import Polyline
from geometry import Polypoint

from dataset import DATASET
from dataset import SERVICE
from intersect import Intersect
from constants import KEY

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        try:
            self._stop_id = int(args.stop_id)
        except:
            self._stop_id = None

        self._markers = args.markers
        self._dataset = args.dataset
        self._buffer = args.buffer_method
        self._dataman = dataman_factory(self._dataset, link_stops=True, link_route_shapes=True)

    def run(self):


        if self._stop_id is None:
            plotter = Plotter()
            polypoint = Polyline()

            routes = self._dataman.get_routes()
            for route in routes:
                segments = route.get_segments()

                for segment in segments:
                    segment.set_attribute(ATTR.STROKE_COLOR, "#0000ff")
                    segment.set_attribute(ATTR.STROKE_WEIGHT, 3)
                    segment.set_attribute(ATTR.STROKE_OPACITY, 0.8)
                    plotter.add_polyline(segment)

            stops = self._dataman.get_active_stops()

            for stop in stops:
                polypoint.add_point(stop.get_point())
                if self._markers:
                    m1 = "%d - 1" % stop.get_id()
                    m2 = "%d - 2" % stop.get_id()
                    plotter.add_marker(stop.get_point(), m1, m2)

            polypoint.set_attribute(ATTR.FILL_OPACITY, 0.8)
            polypoint.set_attribute(ATTR.RADIUS, 90)
            plotter.add_polypoint(polypoint)

            print "Active stops:", len(stops)

            plotter.plot("temp/maps/stop_locations_%s.html" % self._date)
        else:

            plotter = Plotter()
            stop = self._dataman.get_stop(self._stop_id)
            m1 = "%s" % repr(stop.get_id())
            plotter.add_marker(stop.get_point(), m1, m1)

            if self._buffer:
                intersect = Intersect()
                all_stops = self._dataman.get_stops()

                intersect.load(self._buffer, self._dataset, all_stops)
                intersecting_das = intersect.get_intersections_for_group1_id(stop.get_id())

                for item in intersecting_das:
                    p = item[0]
                    plotter.add_polygon(p)

                plotter.plot("temp/maps/stop_%d_buffer_%s_%s" % (stop.get_id(), self._buffer, self._dataset))
            else:
                point = Polypoint()
                point.add_point(stop.get_point())
                plotter.add_polypoint(point)
                plotter.plot("temp/maps/stop_%d_%s" % (stop.get_id(), self._buffer, self._dataset))

            if self._dataset in [DATASET.JULY, DATASET.JUNE]:
                departures = self._dataman.get_departures(stop.get_id(), SERVICE.MWF)
                for departure in departures:
                    # print repr(departure)
                    depart_sec = departure.get(KEY.DEPART_TIME)
                    depart_str = seconds_to_depart_time(depart_sec)
                    direction = departure.get(KEY.DIRECTION)
                    route_id = departure.get(KEY.ROUTE_ID)
                    sign = departure.get(KEY.HEADSIGN)

                    print "%6s Direction: %s Route: %d   %s" % \
                          (depart_str, direction, route_id, sign)


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Plot all stops')
   parser.add_argument("-s", "--stop_id", help="Stop ID", type=int)
   parser.add_argument("-d", "--dataset", help="june/july/brt", type=str, required=True)
   parser.add_argument("-b", "--buffer_method", help="buffer method", type=str, required=False)
   parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()

