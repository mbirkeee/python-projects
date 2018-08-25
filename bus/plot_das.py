import argparse

from data_manager import DataManager
from da_manager import DaData

from plotter import Plotter
from plotter import ATTR

from intersect import Intersect
from modes import BUFFER_LIST
from modes import BUFFER_METHOD

# from my_utils import base_path_from_date

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        # self._markers = args.markers
        # self._all_markers = args.all_markers

        self._da_id = args.da_id
        self._raster_flag = args.rasters
        self._marker_flag = args.markers
        self._buffer_method = args.buffer_method
        self._dataset = args.dataset

        self._dataman = DataManager(self._dataset, link_route_shapes=False, link_stops=False)
        self._daman = DaData()

        self._plot_stops = False

    def run(self):

        plotter = Plotter()

        # saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        # plotter.add_polygon(saskatoon_bb)

        if self._da_id is None:
            das = self._daman.get_das()
            file_name = "temp/maps/das_all.html"

        else:
            das = [self._daman.get_da(self._da_id)]
            file_name = "temp/maps/da_%d.html" % self._da_id
            da = das[0]
            p = da.get_polygon()
            self._plot_stops = True

            if self._buffer_method not in BUFFER_LIST:
                for buffer_method in BUFFER_LIST:
                    print "Valid buffer method: %s" % buffer_method
                raise ValueError("Need valid buffer method")
            intersect = Intersect()

            all_stops = self._dataman.get_stops()
            intersect.load(self._buffer_method, self._dataset, all_stops)

            intersecting_stops = intersect.get_intersections_for_group2_id(da.get_id())

            for stop_tuple in intersecting_stops:
                p = stop_tuple[0]
                stop_id = stop_tuple[1]
                print stop_tuple
                plotter.add_polygon(p)
                if self._marker_flag:
                    title = "%d" % stop_id
                    plotter.add_marker(p.get_centroid(), title, title)

                    stop = self._dataman.get_stop(stop_id)
                    plotter.add_marker(stop.get_point(), title, title)

                    if self._buffer_method == BUFFER_METHOD.CIRCLE_400:
                        stop.make_round_buffer(400)
                        stop_p = stop.get_buffer()
                        stop_p.set_attribute(ATTR.FILL_OPACITY, 0)
                        plotter.add_polygon(stop_p)


        for da in das:
            p = da.get_polygon()
            p.set_attribute(ATTR.FILL_COLOR, "#0000ff")
            plotter.add_polygon(p)

            p2 = da.get_clipped_polygon()
            p2.set_attribute(ATTR.FILL_COLOR, "#0000ff")
            plotter.add_polygon(p2)

            if self._marker_flag:
                centroid = p.get_centroid()
                title = "%d" % da.get_id()
                hover = "hover"
                plotter.add_marker(centroid, title, hover)

            if self._raster_flag:
                rasters = da.get_rasters(100)
                for raster in rasters:
                    p = raster.get_polygon()
                    p.set_attribute(ATTR.FILL_OPACITY, 0)
                    plotter.add_polygon(p)



        plotter.plot(file_name)


            # test_dict = {}
            # if isinstance(segments, list):
            #     for i, segment in enumerate(segments):
            #         test_dict[i] = segment
            #     segments = test_dict
            #
            # # Plot the stops for this route
            # stops = route.get_stops()
            # plotter.add_stops(stops, fillOpacity=0.2)
            # plotter.add_stops(stops, radius=650.0/2.0, fillOpacity=0.1)
            #
            # added_stops = route.get_stops_added()
            # plotter.add_stops(added_stops, radius=30, fillColor="#0000ff", fillOpacity=0.3)
            #
            # removed_stops = route.get_stops_removed()
            # plotter.add_stops(removed_stops, radius=25, fillColor="#808080", fillOpacity=0.4)
            #
            # if self._all_markers:
            #     self._markers = True
            #     stops = self.all_stops_close(self._dataman.get_stops(), stops)
            #
            # if self._markers:
            #
            #     for stop in stops:
            #         msg = "LAT: %f LNG: %f" % (stop.get_lat(), stop.get_lng())
            #         plotter.add_marker(stop.get_point(), stop.get_id(), msg)
            #
            # plotter.add_route(route)
            #
            # plotter.plot("temp/maps/dataset_%s_route_%d.html" % (self._dataset, int(self._route_id)))
            #
            # print "Route: %d (%d - %s) has %d stops" % \
            #       (route.get_id(), route.get_number(), route.get_name(), len(route.get_stops()))
            #
            # # for segment_id, segment in segments.iteritems():
            # #     plotter = Plotter()
            # #     color = "#0000ff"
            # #     segment.set_attribute(ATTR.STROKE_COLOR, color)
            # #     segment.set_attribute(ATTR.STROKE_WEIGHT, 2)
            # #     plotter.add_polyline(segment)
            # #     plotter.plot("temp/maps/segment_%d.html" % segment_id)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot Dissemination Areas')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    parser.add_argument("-a", "--da_id", help="DA ID", type=int)
    parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
    parser.add_argument("-r", "--rasters", help="Include rasters", required=False, action='store_true')
    parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=False, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()

