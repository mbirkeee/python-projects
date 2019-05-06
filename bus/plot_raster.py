import argparse
import random

from data_manager import dataman_factory
from da_manager import DaData

from plotter import Plotter
from plotter import ATTR

from intersect import Intersect
from make_stop_intersections import BufferManager

from modes import BUFFER_METHOD
from modes import BUFFER_LIST

# from my_utils import base_path_from_date

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        self._da_id = args.da_id
        self._raster_id = args.raster_id
        self._marker_flag = args.markers
        self._buffer_method = args.buffer_method
        self._dataset = args.dataset

        self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=True)

        self._daman = DaData()


    def run(self):

        all_stops = self._dataman.get_active_stops()

        print "stop count", len(all_stops)


        file_name = "temp/maps/da_%d_raster_%d.html" % (self._da_id, self._raster_id)

        plotter = Plotter()

        da = self._daman.get_da(self._da_id)

        intersect = Intersect()
        intersect.load(self._buffer_method, self._dataset, all_stops)
        intersecting_stops = intersect.get_intersections_for_group2_id(self._da_id)

        buffer_man = None
        if self._buffer_method in [BUFFER_METHOD.NETWORK_400, BUFFER_METHOD.NETWORK_2000]:
            buffer_man = BufferManager(self._buffer_method, self._dataset)

        # for stop_tuple in intersecting_stops:
        #     p = stop_tuple[0]
        #     stop_id = stop_tuple[1]
        #     stop = self._dataman.get_stop(stop_id)
        #     print "repr(stop)", repr(stop)
        #     print dir(stop)
        #     stop.make_buffer(self._buffer_method, buffer_manager=buffer_man)
        #
        #
        #     b = stop.get_buffer()
        #     plotter.add_polygon(b)

        p = da.get_polygon()
        p.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        p.set_attribute(ATTR.FILL_OPACITY, 0.2)
        plotter.add_polygon(p)

        rasters = da.get_rasters(100)
        for raster in rasters:

            if raster.get_id() == self._raster_id:
                rp = raster.get_polygon()
                rp.set_attribute(ATTR.FILL_COLOR, "#0000ff")
                rp.set_attribute(ATTR.FILL_OPACITY, 0.5)
                plotter.add_polygon(rp)


                for stop_tuple in intersecting_stops:
                    stop_id = stop_tuple[1]
                    stop = self._dataman.get_stop(stop_id)
                    stop.make_buffer(self._buffer_method, buffer_manager=buffer_man)

                    buffer = stop.get_buffer()
                    if rp.intersects(buffer):
                        plotter.add_polygon(buffer)

                        # polypoint.add_point(stop.get_point())

                        m1 = "%d" % stop.get_id()
                        m2 = "%d" % stop.get_id()
                        plotter.add_marker(stop.get_point(), m1, m2)

        plotter.plot(file_name)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot One Raster')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    parser.add_argument("-a", "--da_id", help="DA ID", type=int, required=True)
    parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
    parser.add_argument("-r", "--raster_id", help="The raster to plot", type=int, required=True)
    parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=True, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()

