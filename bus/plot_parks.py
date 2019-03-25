import argparse
import shapefile

from data_manager import dataman_factory
from da_manager import DaData


from plotter import Plotter
from plotter import ATTR

from intersect import Intersect

from geometry import Polygon
from geometry import Point

# from modes import BUFFER_METHOD
# from modes import BUFFER_LIST

# from my_utils import base_path_from_date

class Runner(object):
    """
    This program plots City of Saskatoon parks
    """
    def __init__(self, args):

        # self._markers = args.markers
        # self._all_markers = args.all_markers

        # self._da_id = args.da_id
        # self._raster_flag = args.rasters
        # self._marker_flag = args.markers
        # self._buffer_method = args.buffer_method
        # self._dataset = args.dataset

        # self._dataman = DataManager(self._dataset, link_route_shapes=False, link_stops=False)
        # self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=False)

        self._daman = DaData()

        # self._plot_stops = False
        self._da_id = None
        self._park_polygons = {}

        pass

    def read_parks_shapefile(self, filename):

        print "I want to read this file name", filename

        sf = shapefile.Reader(filename)

        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        print "from_shapefile(): Loaded %d records" % len(records)

        # This loop converts the loaded shapefile data itn "rasters"
        for i, record in enumerate(records):

            fid = record[0]
            name = record[2]
            kind = record[3]

            if fid == 121:
                print repr(record)

            # da_id = record[1]
            # raster_id = record[2]
            # score = record[3]

            shape = shapes[i]

            if fid == 121 or fid == 122:
                print "------------------------------------"
                print repr(shape)
                print len(shape.points)
                print dir(shape)

                print shape.parts, shape.shapeType

            # if fid != 121: continue

            if len(shape.parts) != 1:
                print "more than one polygon!!!", fid, shape.parts

            polygon = None
            part_index = 0

            for index in xrange(len(shape.points)-1):

                try:
                    if index == shape.parts[part_index]:
                        print "FOUND START", part_index, index
                        if polygon:
                            # Save existing polygons
                            self.save_polygon(polygon, fid, name, kind, part_index)
                            polygon = None

                        if polygon is None:
                            # Allocate a new polygon
                            polygon = Polygon()

                        part_index += 1

                except Exception as err:
                    print "Exception", repr(err)

                item = shape.points[index]
                # print item
                polygon.add_point(Point(item[0], item[1]))

            if polygon:
                self.save_polygon(polygon, fid, name, kind, part_index)

        for key, value in self._park_polygons.iteritems():
            print key, value

    def save_polygon(self, polygon, fid, name, kind, part_index):
        area = polygon.get_area()
        # print "Park Area:", area
        key = "%d-%d" % (fid, part_index)

        print "SAVING POLYGON", key

        self._park_polygons[key] = {
            "name"  : name,
            "kind"  : kind,
            "poly"  : polygon
        }

            # raster = Raster(da_id, raster_id, polygon)
            # raster.set_score(score)
            #
            # self._raster_list.append(raster)

    def run(self, filename):

        self.read_parks_shapefile(filename)

        # raise ValueError("stop here")

        plotter = Plotter()

        # saskatoon_bb = self._daman.get_saskatoon_bounding_box()
        # plotter.add_polygon(saskatoon_bb)

        if self._da_id is None:
            das = self._daman.get_das()
            file_name = "temp/maps/parks_all.html"

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

                    stop.make_buffer(BUFFER_METHOD.CIRCLE_400)
                    stop_p = stop.get_buffer()
                    stop_p.set_attribute(ATTR.FILL_OPACITY, 0)
                    plotter.add_polygon(stop_p)

        total_raster_count = 0


        for park_id, park_data in self._park_polygons.iteritems():
            park_p = park_data.get("poly")

            # if park_id != 121: continue

            park_p.set_attribute(ATTR.FILL_COLOR, "#00ff00")
            park_p.set_attribute(ATTR.FILL_OPACITY, 0.8)

            plotter.add_polygon(park_p)

        #    centroid = park_p.get_centroid()
        #    hover = "hover"
            title = "%s" % repr(park_id)

            # print centroid
        #    title = "%s %s" % (park_data.get("name"), repr(park_data.get("kind")))

         #   print title

         #   plotter.add_marker(centroid, title, hover)

        for da in das:
            p = da.get_polygon()
            p.set_attribute(ATTR.FILL_COLOR, "#0000ff")
            plotter.add_polygon(p)

            p2 = da.get_clipped_polygon()
            p2.set_attribute(ATTR.FILL_COLOR, "#0000ff")
            plotter.add_polygon(p2)

            # if self._marker_flag:
            #     centroid = p.get_centroid()
            #     title = "%d" % da.get_id()
            #     hover = "hover"
            #     plotter.add_marker(centroid, title, hover)
            #
            # if self._raster_flag:
            #     rasters = da.get_rasters(100)
            #     for raster in rasters:
            #         p = raster.get_polygon()
            #         p.set_attribute(ATTR.FILL_OPACITY, 0)
            #         plotter.add_polygon(p)
            #         total_raster_count += 1

        plotter.plot(file_name)

        print "park polygons:", len(self._park_polygons)


        park_area_dict = {}
        total_area_dict = {}

        for da in das:
            da_id = da.get_id()
            park_area_dict[da_id] = 0.0

            da_p = da.get_clipped_polygon()
            total_area_dict[da_id] = da_p.get_area()

            for pid, park_data in self._park_polygons.iteritems():
                park_p = park_data.get("poly")

                intersections = da_p.intersect(park_p)


                if not intersections:
                    # print "------> NO"
                    pass
                else:
                    print "len intersections", len(intersections)
                    for intersection in intersections:
                        print "======> YES", intersection.get_area()

                        area = park_area_dict.get(da_id)
                        area += intersection.get_area()
                        park_area_dict[da_id] = area

        for da_id, total_area in total_area_dict.iteritems():
            park_area = park_area_dict.get(da_id)
            pcent = 100.0 * (park_area / total_area)

            print "DA ID: %d TOTAL %f PARK %f PERCENT %f" % (da_id, total_area, park_area, pcent)
        # if total_raster_count > 0:
        #     print "Plotted %d rasters" % total_raster_count

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Plot Parks')
    # parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    # parser.add_argument("-a", "--da_id", help="DA ID", type=int)
    # parser.add_argument("-m", "--markers", help="Include stop markers (slow and messy)", required=False, action='store_true')
    # parser.add_argument("-r", "--rasters", help="Include rasters", required=False, action='store_true')
    # parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=False, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run("data/shapefiles/parks/COS_Parks.shp")

