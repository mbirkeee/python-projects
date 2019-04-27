import argparse
import random
import scipy as sp

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

        # self._markers = args.markers
        # self._all_markers = args.all_markers

        self._da_id = args.da_id
        self._raster_id = args.raster_id
        self._marker_flag = args.markers
        self._buffer_method = args.buffer_method
        self._dataset = args.dataset

        self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=True)

        self._daman = DaData()


    def add_da(self, da_id, plotter, all_stops):

        das = [self._daman.get_da(da_id)]
        da = das[0]
        p = da.get_polygon()
        self._plot_stops = True

        if self._buffer_method not in BUFFER_LIST:
            for buffer_method in BUFFER_LIST:
                print "Valid buffer method: %s" % buffer_method
            raise ValueError("Need valid buffer method")

        intersect = Intersect()
        intersect.load(self._buffer_method, self._dataset, all_stops)
        intersecting_stops = intersect.get_intersections_for_group2_id(da.get_id())

        for stop_tuple in intersecting_stops:
            p = stop_tuple[0]
            stop_id = stop_tuple[1]

            if stop_id == 5913: continue
            print stop_tuple
            plotter.add_polygon(p)
            if self._marker_flag:
                title = "%d" % stop_id
                plotter.add_marker(p.get_centroid(), title, title)

                stop = self._dataman.get_stop(stop_id)

                plotter.add_marker(stop.get_point(), title, title)

                stop.make_buffer(BUFFER_METHOD.CIRCLE_400)
                stop_p = stop.get_buffer()
                stop_p.set_attribute(ATTR.FILL_OPACITY, 0)
                plotter.add_polygon(stop_p)

        da = self._daman.get_da(da_id)

        print "DA area:", da.get_area()
        print "DA population", da.get_population()
        print "DA transit", da.get_percent_transit_users()

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



        # # This hack gets rid of the valley road stop
        # # all_stops_filtered = []
        # # for stop in all_stops:
        # #     # print repr(stop)
        # #     print stop.get_id()
        # #     if stop.get_id() == 5913:
        # #         continue
        # #     all_stops_filtered.append(stop)
        #
        # # saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        # # plotter.add_polygon(saskatoon_bb)
        #
        # if self._da_id is None:
        #     das = self._daman.get_das()
        #     file_name = "temp/maps/das_all.html"
        #
        # else:
        #
        #
        #     das = []
        #
        #     for da_id in self._da_list:
        #         das.append(self._daman.get_da(da_id))
        #         self.add_da(da_id, plotter, all_stops)
        #
        #
        #
        # total_raster_count = 0
        # for da in das:
        #     p = da.get_polygon()
        #     p.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        #
        #     random_opacity = float(random.randint(0,1000))/1000.0
        #     random_opacity = 0.20 + 0.2 * random_opacity
        #     p.set_attribute(ATTR.FILL_OPACITY, random_opacity)
        #     plotter.add_polygon(p)
        #
        #     # p2 = da.get_clipped_polygon()
        #     # p2.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        #     # plotter.add_polygon(p2)
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
        #
        #             print "DA ID %s RASTER ID %s" % (da.get_id(), raster.get_id())
        #
        #             p = raster.get_polygon()
        #             p.set_attribute(ATTR.FILL_OPACITY, 0)
        #             plotter.add_polygon(p)
        #             total_raster_count += 1

        plotter.plot(file_name)


    def da_stats(self):

        das = self._daman.get_das()

        size_before = []
        size_after = []

        result = []
        for da in das:

            da_id = da.get_id()
            area = da.get_area()/1000000.0

            size_before.append(area)

            total_raster_area = 0
            rasters = da.get_rasters(100)
            for raster in rasters:
                p = raster.get_polygon()
                a = p.get_area()
                total_raster_area += a
            # print da_id, area

            total_raster_area = total_raster_area / 1000000.0
            size_after.append(total_raster_area)

            diff = abs(area-total_raster_area)
            pcent = 100 * diff/area
            result.append((area, total_raster_area, diff, pcent, da_id))

        result.sort()

        f = open("cumulative_da_area.csv", "w")
        f.write("da_id,c1,c2\n")

        c1 = c2 = 0
        for index,item in enumerate(result):
            c1 += item[0]
            c2 += item[1]
            f.write("%d,%d,%f,%f\n" % (item[4], index + 1, c1, c2))
        f.close()

        result.reverse()
        f = open("da_area.csv", "w")

        f.write("da_id,area_before,area_after,diff,pcent\n")
        for item in result:
            f.write("%d,%f,%f,%f,%f\n" % (item[4], item[0], item[1], item[2], item[3]))
        f.close()

        print "The number of DAs is:", len(result)

        print "before"
        print "ave", sp.average(size_before)
        print "med", sp.median(size_before)
        print "std", sp.std(size_before)
        print "sum", sp.sum(size_before)

        print "after"
        print "ave", sp.average(size_after)
        print "med", sp.median(size_after)
        print "std", sp.std(size_after)
        print "sum", sp.sum(size_after)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot Dissemination Areas')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    parser.add_argument("-a", "--da_id", help="DA ID", type=int, required=True)
    parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
    parser.add_argument("-r", "--raster_id", help="The raster to plot", type=int, required=True)
    parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=True, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()

