import argparse

from data_manager import dataman_factory
from da_manager import DaData

from plotter import Plotter
from plotter import ATTR

from intersect import Intersect

from modes import BUFFER_METHOD
from modes import BUFFER_LIST

# from my_utils import base_path_from_date

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        # self._markers = args.markers
        # self._all_markers = args.all_markers

        # self._da_id = args.da_id
        # self._raster_flag = args.rasters
        # self._marker_flag = args.markers
        # self._buffer_method = args.buffer_method
        self._dataset = args.dataset

        # self._dataman = DataManager(self._dataset, link_route_shapes=False, link_stops=False)
        self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=True)
        self._daman = DaData()

        self._plot_stops = False

    def run(self):

        plotter = Plotter()

        # saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        # plotter.add_polygon(saskatoon_bb)

        all_stops = self._dataman.get_active_stops()
        all_rasters = self._daman.get_all_rasters(all_stops)


        for raster in all_rasters:
            p = raster.get_polygon()
            plotter.add_polygon(p)

        plotter.plot("temp/maps/all_rasters_%s.html" % self._dataset)

        print "Len active stops", len(all_stops)
        print "Len rasters", len(all_rasters)

        raise ValueError('temp stop')
        # if self._da_id is None:
        #     das = self._daman.get_das()
        #     file_name = "temp/maps/das_all.html"
        #
        # else:
        #     das = [self._daman.get_da(self._da_id)]
        #     file_name = "temp/maps/da_%d.html" % self._da_id
        #     da = das[0]
        #     p = da.get_polygon()
        #     self._plot_stops = True
        #
        #     if self._buffer_method not in BUFFER_LIST:
        #         for buffer_method in BUFFER_LIST:
        #             print "Valid buffer method: %s" % buffer_method
        #         raise ValueError("Need valid buffer method")
        #
        #     intersect = Intersect()
        #
        #     # all_stops = self._dataman.get_stops()
        #     all_stops = self._dataman.get_stops()
        #     intersect.load(self._buffer_method, self._dataset, all_stops)
        #
        #     intersecting_stops = intersect.get_intersections_for_group2_id(da.get_id())
        #
        #     for stop_tuple in intersecting_stops:
        #         p = stop_tuple[0]
        #         stop_id = stop_tuple[1]
        #         print stop_tuple
        #         plotter.add_polygon(p)
        #         if self._marker_flag:
        #             title = "%d" % stop_id
        #             plotter.add_marker(p.get_centroid(), title, title)
        #
        #             stop = self._dataman.get_stop(stop_id)
        #             plotter.add_marker(stop.get_point(), title, title)
        #
        #             stop.make_buffer(BUFFER_METHOD.CIRCLE_400)
        #             stop_p = stop.get_buffer()
        #             stop_p.set_attribute(ATTR.FILL_OPACITY, 0)
        #             plotter.add_polygon(stop_p)
        #
        # total_raster_count = 0
        # for da in das:
        #     p = da.get_polygon()
        #     p.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        #     plotter.add_polygon(p)
        #
        #     p2 = da.get_clipped_polygon()
        #     p2.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        #     plotter.add_polygon(p2)
        #
        #     if self._marker_flag:
        #         centroid = p.get_centroid()
        #         title = "%d" % da.get_id()
        #         hover = "hover"
        #         plotter.add_marker(centroid, title, hover)
        #
        #     if self._raster_flag:
        #         rasters = da.get_rasters(100)
        #         for raster in rasters:
        #             p = raster.get_polygon()
        #             p.set_attribute(ATTR.FILL_OPACITY, 0)
        #             plotter.add_polygon(p)
        #             total_raster_count += 1
        #
        # plotter.plot(file_name)
        # if total_raster_count > 0:
        #     print "Plotted %d rasters" % total_raster_count

        self.da_stats()

    def da_stats(self):

        das = self._daman.get_das()

        result = []
        for da in das:

            da_id = da.get_id()
            area = da.get_area()

            total_raster_area = 0
            rasters = da.get_rasters(100)
            for raster in rasters:
                p = raster.get_polygon()
                a = p.get_area()
                total_raster_area += a
            # print da_id, area
            diff = abs(area-total_raster_area)

            result.append((area, total_raster_area, diff, da_id))


        result.sort(reverse=True)


        for item in result:
            print item

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot All Rasters Areas')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    # parser.add_argument("-a", "--da_id", help="DA ID", type=int)
    # parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
    # parser.add_argument("-r", "--rasters", help="Include rasters", required=False, action='store_true')
    # parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=False, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()

