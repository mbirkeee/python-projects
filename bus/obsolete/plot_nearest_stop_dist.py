import argparse

from da_manager import DaData
from data_manager import dataman_factory

from plotter import Plotter
from plotter import ATTR

class Runner(object):

    def __init__(self, args):

        self._dataset = args.dataset
        self._method = args.method

        self._daman = DaData()
        self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=True)

    def run(self):

        plotter = Plotter()

        saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        plotter.add_polygon(saskatoon_bb)

        active_stops = self._dataman.get_active_stops()

        result = []

        das = self._daman.get_das()
        for da in das:
            rasters = da.get_rasters(100)
            # print "# of rasters:", len(rasters)
            for raster in rasters:
                min_dist, min_stop = raster.get_closest_stop(active_stops, method=self._method)
                result.append((raster, min_dist))

        total_dist = 0
        for item in result:
            dist = item[1]
            raster = item[0]
            total_dist += dist

            p = raster.get_polygon()
            opacity = 1 - dist / 500.0
            if opacity < 0:
                opacity = 0

            p.set_attribute(ATTR.FILL_COLOR, "#ff0000")
            p.set_attribute(ATTR.FILL_OPACITY, opacity)
            p.set_attribute(ATTR.STROKE_WEIGHT, 0)
            p.set_attribute(ATTR.STROKE_COLOR, "#202020")
            p.set_attribute(ATTR.STROKE_OPACITY, 0)
            plotter.add_polygon(p)

        print "Ave dist:", total_dist / float(len(result))

        plotter.plot("temp/maps/plot_distance_%s_%s.html" % (self._dataset, self._method))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Compute and plot ave dist to closest stop')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    parser.add_argument("-m", "--method", help="Distance method: grid/crow", type=str, required=True)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()
