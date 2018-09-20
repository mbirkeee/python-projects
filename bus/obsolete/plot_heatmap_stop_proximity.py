import argparse
import my_utils
import pyproj
import random
import time

from constants import BASE
from constants import DATASET
from constants import MODE

from da_manager import DaData
from data_manager import DataManager

# from transit_shapes import TransitShapes
# from stop_times import TransitTrips
from intersect import Intersect
from my_utils import Filter

from heatmap import Heatmap
from plotter import Plotter
from plotter import ATTR

from geometry import Polyline
from geometry import Polypoint

from shapefile_writer import ShapeFileWriter
from score import Score

from my_utils import base_path_from_date

class Runner(object):
    """
    This program generates and plots a heatmap for proximity to stops
    """
    def __init__(self, args):

        try:
            self._plot_route_ids = [int(args.route_id)]
        except:
            self._plot_route_ids = []

        self._date = args.date
        self._base_path = base_path_from_date(args.date)

    def run(self):

        dataman = DataManager(self._base_path)
        da_mgr = DaData()
        das = da_mgr.get_das()

        if True:
            da_id_list = [
                47110049,
                47110045,
                47110046,
                47110065,
            ]

            das = []
            for da_id in da_id_list:
                das.append(da_mgr.get_da(da_id))

        heatmap = Heatmap()

        print "Plotting Proximity heatmap --------------------------------------"

        # Make a list of all routes to plot
        plot_routes = []
        routes = dataman.get_routes()
        for route in routes:
            consider = False
            if not self._plot_route_ids:
                consider  = True
            else:
                if route.get_id() in self._plot_route_ids:
                    consider = True
            if consider:
                plot_routes.append(route)
                print "Including route", route.get_id(), route.get_name()
            else:
                print "Skipping route", route.get_id(), route.get_name()

        # Make a list of stops to consider
        stop_ids = []
        for route in plot_routes:
            stop_ids.extend(route.get_stop_ids())

        print "Stop list len", len(stop_ids)
        stop_ids = list(set(stop_ids))
        print "Stop list len (no duplicates)", len(stop_ids)

        mode = MODE.ONE
        stops = []
        for stop_id in stop_ids:
            stop = dataman.get_stop(stop_id)
            stop.make_round_buffer(400)
            stops.append(stop)

        # Even though logically I would like to perform the intersection in the
        # call to compute demand, it is more efficient to do it here because the
        # results are used again later on

        intersect = Intersect()
        intersect.load(mode, DATASET.JUNE)

        # try:
        #     print "Successfully read intersections from shapefile"
        #
        # except Exception as err:
        #     print "Exception: %s" % repr(err)
        #     intersect.process(stops, das)
        #     intersect.to_shapefile(mode, DATASET.JUNE)

        judge = Score(dataman)

        plot_rasters = []
        for da in das:
            rasters = da.get_rasters(100)
            stop_tuples = intersect.get_intersections(group=2, id=da.get_id())
            print "Got %d stops for da_id: %d" % (len(stop_tuples), da.get_id())

            for raster in rasters:
                score = judge.get_score_stop_count(raster, stop_tuples)
                if score > 0:
                    raster.set_score(score)
                    plot_rasters.append(raster)
                    heatmap.add_raster(raster)

        shapefile_name = "temp/shapefiles/stop_proximity_mode_%s_%s.shp" % (mode, self._date)
        heatmap.to_shapefile(shapefile_name)
        heatmap.plot("temp/maps/stop_proximity_mode_%s_date_%s.html" % (mode, self._date), das=das)

    def test3(self):

        heatmap = Heatmap()
        heatmap.set_mode(MODE.ONE)
        heatmap.set_dataset(DATASET.JUNE)
        heatmap.run()
        heatmap.plot()
        heatmap.to_shapefile("temp/temp_heatmap.shp")

    def test_heatmap_subtraction(self):

        shapefile_name = "temp/shapefiles/stop_proximity_sq_wd_jun.shp"
        heatmap1 = Heatmap()
        heatmap1.from_shapefile(shapefile_name)
        # heatmap1.plot("temp/maps/stop_proximity_jun.html")

        shapefile_name = "temp/shapefiles/stop_proximity_jun.shp"
        heatmap2 = Heatmap()
        heatmap2.from_shapefile(shapefile_name)
        # heatmap2.plot("temp/maps/stop_proximity_jul.html")

        da_mgr = DaData()

        heatmap3 = heatmap2 - heatmap1
        heatmap3.plot("temp/maps/stop_proximity_jun_cir_sq_decay.html", das=da_mgr.get_das())

    def test2(self):

        da_mgr = DaData()

        start_time = time.time()
        for da in da_mgr.get_das():
            rasters = da.get_rasters(100)
            print "DA id: %d len(rasters): %d" % (da.get_id(), len(rasters))

        print "Elapsed time:", time.time() - start_time

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Heatmap - Proximity to stops')
    parser.add_argument("-r", "--route_id", help="Route ID", type=int)
    parser.add_argument("-d", "--date", help="june/july/brt", type=str, required=True)
    parser.add_argument("-m", "--mode", help="score mode", type=str, required=True)
    args = parser.parse_args()

    runner = Runner(args)
    # runner.run()
    runner.test3()

    # runner.test1()

