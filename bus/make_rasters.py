import argparse

from da_manager import DaData
from data_manager import dataman_factory

from plotter import Plotter
from geometry import Polyline

class Runner(object):

    def __init__(self, args):

        self._daman = DaData()
        self._dataman = dataman_factory("july", link_route_shapes=False, link_stops=True)

    def run(self):

        plotter = Plotter()
        polypoint = Polyline()

        # saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        # plotter.add_polygon(saskatoon_bb)

        # To speed things up, make a list of all stops and throw away any raster
        # points that are farther than 1 km from the nearest stop.
        all_stops = self._dataman.get_active_stops()

        self._daman.make_rasters(all_stops)
        all_rasters = self._daman.get_all_rasters(all_stops)

        for raster in all_rasters:
            p = raster.get_polygon()
            plotter.add_polygon(p)

        for stop in all_stops:
            polypoint.add_point(stop.get_point())
            # stop.make_buffer(self._buffer, buffer_manager=buffer_man)
            # buf = stop.get_buffer()
            # plotter.add_polygon(buf)
        plotter.add_polypoint(polypoint)
        plotter.plot("temp/maps/make_rasters.html")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Make Dissemination Areas Rasters')
    # parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()
