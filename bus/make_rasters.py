import argparse

from da_manager import DaData
from data_manager import DataManager

from plotter import Plotter

class Runner(object):

    def __init__(self, args):

        self._daman = DaData()
        self._datamam = DataManager("june",link_route_shapes=False,link_stops=False)

    def run(self):

        plotter = Plotter()

        saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        plotter.add_polygon(saskatoon_bb)

        # To speed things up, make a list of all stops and throw away any raster
        # points that are farther than 1 km from the nearest stop.
        all_stops = self._datamam.get_stops()
        self._daman.make_rasters(all_stops)
        all_rasters = self._daman.get_all_rasters(all_stops)

        for raster in all_rasters:
            p = raster.get_polygon()
            plotter.add_polygon(p)

        plotter.plot("temp/maps/make_rasters.html")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Make Dissemination Areas Rasters')
    # parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    # parser.add_argument("-a", "--da_id", help="DA ID", type=int)
    # parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
    # parser.add_argument("-r", "--rasters", help="Include rasters", required=False, action='store_true')
    # # parser.add_argument("-a", "--all_markers", help="Include ALL stop markers", required=False, action='store_true')

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()
