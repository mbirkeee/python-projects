import argparse

from da_manager import DaData
from data_manager import dataman_factory
from intersect import Intersect

class Runner(object):

    def __init__(self, args):

        self._buffer_method = args.buffer_method
        self._dataset = args.dataset

        self._daman = DaData()
        self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=False)

    def run(self):

        # To speed things up, make a list of all stops and throw away any raster
        # points that are farther than 1 km from the nearest stop.
        all_stops = self._dataman.get_stops()
        das = self._daman.get_das()

        intersect = Intersect()

        try:
            intersect.load(self._buffer_method, self._dataset, all_stops)

        except Exception as err:
            print "Intersect().load() Exception: %s" % repr(err)

            for stop in all_stops:
                stop.make_buffer(self._buffer_method)

            intersect.process(all_stops, das)
            intersect.to_shapefile(self._buffer_method, self._dataset, all_stops)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Make Stop Intersections')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=True, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()
