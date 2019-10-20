import argparse
import random

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
from shapefile_writer import ShapeFileWriter
from da_manager import DaData
from make_stop_intersections import BufferManager

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        try:
            self._stop_id = int(args.stop_id)
        except:
            self._stop_id = None

        self._include_das = args.das
        self._markers = args.markers
        self._dataset = args.dataset
        self._buffer = args.buffer_method
        self._all_stops = args.all_stops

        self._output_shapefile = args.output_shapefile

        self._dataman = dataman_factory(self._dataset, link_stops=True, link_route_shapes=True)

    def run(self):

        print "dataset:", self._dataset
        print "markers", self._markers
        print "buffer", self._buffer
        print "all stops:", self._all_stops
        print "output shapefile", self._output_shapefile

        buffer_man = BufferManager(buffer_method=self._buffer, dataset=self._dataset)

        if self._stop_id is None:

            plotter = Plotter()
            polypoint = Polyline()

            # routes = self._dataman.get_routes()
            # for route in routes:
            #     segments = route.get_segments()
            #
            #     for segment in segments:
            #         segment.set_attribute(ATTR.STROKE_COLOR, "#0000ff")
            #         segment.set_attribute(ATTR.STROKE_WEIGHT, 2)
            #         segment.set_attribute(ATTR.STROKE_OPACITY, 0.5)
            #         plotter.add_polyline(segment)

            if self._all_stops:
                stops = self._dataman.get_stops()
            else:
                stops = self._dataman.get_active_stops()

            for stop in stops:
                polypoint.add_point(stop.get_point())
                if self._markers:
                    m1 = "%d - 1" % stop.get_id()
                    m2 = "%d - 2" % stop.get_id()
                    plotter.add_marker(stop.get_point(), m1, m2)

                stop.make_buffer(self._buffer, buffer_manager=buffer_man)
                buf = stop.get_buffer()
                plotter.add_polygon(buf)

                print "TEMP BREAK AFTER ONE STOP"
                break

            polypoint.set_attribute(ATTR.FILL_OPACITY, 0.5)
            polypoint.set_attribute(ATTR.RADIUS, 60)
            plotter.add_polypoint(polypoint)

            if self._include_das:
                daman = DaData()
                das = daman.get_das()
                plotter.add_das(das)
                # daman = DaData()
                # das = daman.get_das()
                # for da in das:
                #     p = da.get_polygon()
                #     # p.set_attribute(ATTR.FILL_COLOR, color)
                #     # p.set_attribute(ATTR.FILL_OPACITY, opacity)
                #     p.set_attribute(ATTR.STROKE_WEIGHT, 1)
                #     p.set_attribute(ATTR.STROKE_COLOR, "#505050")
                #     # p.set_attribute(ATTR.STROKE_OPACITY, 1)
                #     plotter.add_polygon(p)


            if self._all_stops:
                print "Total Stops:", len(stops)
            else:
                print "Active stops:", len(stops)

            plotter.plot("temp/maps/stop_locations_%s.html" % self._dataset)

            if self._output_shapefile:
                self.to_shapefile(stops)
        else:

            buffer_man_400 = BufferManager(buffer_method="network_400", dataset=self._dataset)
            buffer_man_532 = BufferManager(buffer_method="network_532", dataset=self._dataset)
            daman = DaData()

            plotter = Plotter()
            stop = self._dataman.get_stop(self._stop_id)
            m1 = "%s" % repr(stop.get_id())
            plotter.add_marker(stop.get_point(), m1, m1)

            if self._buffer:
                intersect = Intersect()

                all_stops = self._dataman.get_active_stops()

                intersect.load(self._buffer, self._dataset, all_stops)
                intersecting_das = intersect.get_intersections_for_group1_id(stop.get_id())


                for item in intersecting_das:
                    print "Stop intersects DA:", repr(item)
                    da_id = item[1]
                    da = daman.get_da(da_id)
                    print " - Population", da.get_population()
                    print " - Area", da.get_area()

                    p = item[0]

                    p.set_attribute(ATTR.FILL_COLOR, "#0000ff")
                    p.set_attribute(ATTR.STROKE_WEIGHT, 3)

                    random_opacity = float(random.randint(0,1000))/1000.0
                    random_opacity = 0.20 + 0.5 * random_opacity
                    p.set_attribute(ATTR.FILL_OPACITY, random_opacity)
                    plotter.add_polygon(p)

                    print "intersection DA", da_id, "Area", p.get_area()

                # stop.make_buffer(self._buffer, buffer_manager=buffer_man)
                # buffer_p = stop.get_buffer()
                # plotter.add_polygon(buffer_p)

                stop.make_buffer("circle_400")
                buffer_p = stop.get_buffer()
                plotter.add_polygon(buffer_p)

                # stop.make_buffer("network_400", buffer_manager=buffer_man_400)
                # buffer_p = stop.get_buffer()
                # plotter.add_polygon(buffer_p)

                stop.make_buffer("network_532", buffer_manager=buffer_man_532)
                buffer_p = stop.get_buffer()
                plotter.add_polygon(buffer_p)

                plotter.plot("temp/maps/stop_%d_buffer_%s_%s.html" % (stop.get_id(), self._buffer, self._dataset))
            else:
                point = Polypoint()
                point.add_point(stop.get_point())
                plotter.add_polypoint(point)
                plotter.plot("temp/maps/stop_%d_%s.html" % (stop.get_id(), self._dataset))

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
            else:
                print "Stop serves routes:"
                print "------------------"
                routes = stop.get_routes()
                for route in routes:
                    print "%3d %d   %s" % (route.get_number(), route.get_id(), route.get_name())

    def to_shapefile(self, stops):

        writer = ShapeFileWriter()

        stop_list = []
        for index, stop in enumerate(stops):
            stop_list.append((stop.get_id(), stop))

        stop_list = sorted(stop_list)

        for item in stop_list:
            writer.add_stop(item[1])

        writer.write_stop_file("temp/shapefiles/stop_locations_%s.shp" % self._dataset)


if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Plot all stops')
   parser.add_argument("-s", "--stop_id", help="Stop ID", type=int)
   parser.add_argument("-d", "--dataset", help="june/july/brt", type=str, required=True)
   parser.add_argument("-b", "--buffer_method", help="buffer method", type=str, required=False)
   parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
   parser.add_argument("-i", "--das", help="Include DA outlines", required=False, action='store_true')
   parser.add_argument("-a", "--all_stops", help="Default is just active stops", required=False, action='store_true')
   parser.add_argument("-o", "--output_shapefile", help="Write a stop shapefile", required=False, action='store_true')

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()

