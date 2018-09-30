import os
import shapefile
from shapefile_writer import ShapeFileWriter
from geometry import Polygon
from geometry import Point
from modes import BUFFER_METHOD

class Intersect(object):

    def __init__(self):

        self.group1_data = {}
        self.group2_data = {}

        self.group1 = None
        self.group2 = None

        self._total_count = 0
        self._temp_count = 0

        self._file_name = None

        self._shapefile_name_template = \
            "temp/shapefiles/intersect_cache/stop_buffer_%s_count_%d_dataset_%s.shp"

    def load(self, buffer_type, dataset, stops):

        if buffer_type == BUFFER_METHOD.NONE:
            print "Intersect.load(): skipping intersection calculation"
            return

        stop_count = len(stops)
        file_name = self._shapefile_name_template % (buffer_type, stop_count, dataset)
        self.from_shapefile(file_name)

    def from_shapefile(self, file_name):

        if not os.path.exists(file_name):
            raise ValueError("File does not exist: %s" % file_name)

        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        # print "len(records)", len(records)
        # print "len(shapes)", len(shapes)

        for i, record in enumerate(records):
            fid = record[0]
            group1_id = record[1]
            group2_id = record[2]

            shape = shapes[i]

            polygon = Polygon()
            for index in xrange(len(shape.points)-1):
                item = shape.points[index]
                polygon.add_point(Point(item[0], item[1]))

            # Add to group 1
            data = self.group1_data.get(group1_id, {})
            data2 = data.get(group2_id, [])
            data2.append(polygon)
            data[group2_id] = data2
            self.group1_data[group1_id] = data

            # Add to group 2
            data = self.group2_data.get(group2_id, {})
            data2 = data.get(group1_id, [])
            data2.append(polygon)
            data[group1_id] = data2
            self.group2_data[group2_id] = data

        print "Read %d intersections from %s" % (len(records), file_name)

    def to_shapefile(self, buffer_type, dataset, stops):

        file_name = self._shapefile_name_template % (buffer_type, len(stops), dataset)

        writer = ShapeFileWriter()

        intersection_list = []
        print "Save intersections to file: %s" % file_name
        for group1_id, data in self.group1_data.iteritems():
            for group2_id, intersecting_polygons in data.iteritems():
                for p in intersecting_polygons:
                    # print "write to shapefile:", group1_id, group2_id, p.get_area()
                    intersection_list.append((group1_id, group2_id, p))

        writer.write_stop_da_intersections(intersection_list, file_name)

    def _count(self):
        self._total_count += 1
        self._temp_count += 1
        if self._temp_count >= 1000:
            print "Detected %d intersections..." % self._total_count
            self._temp_count = 0

    def process(self, group1, group2, limit=None):

        if not isinstance(group1, list):
            group1 = [group1]

        if not isinstance(group2, list):
            group2 = [group2]

        print "Computing intersections:"
        print "group1 items: %d" % len(group1)
        print "group2 items: %d" % len(group2)

        temp_count = 0
        for item1 in group1:
            group1_id = item1.get_id()
            polygon_1 = item1.get_polygon()

            if polygon_1 is None:
                raise ValueError("No polygon for item1: %s" % type(item1))
            # self._group1_id_map[group1_id] = item1

            # print "finding intersections for group1 id:", group1_id

            for item2 in group2:
                group2_id = item2.get_id()
                polygon_2 = item2.get_polygon()

                if polygon_2 is None:
                    raise ValueError("No polygon for item2: %s" % type(item2))
                # self._group2_id_map[group2_id] = item2

                # print "    compare to group2 id:", group2_id, polygon_2.get_area()
                # Do these polygons intersect?

                intersection = polygon_1.intersect(polygon_2)

                if intersection:
                    data = self.group1_data.get(group1_id, {})
                    data2 = data.get(group2_id, [])
                    for p in intersection:
                        # print "  poly2 intersects poly1", p.get_area()
                        data2.append(p)
                        self._count()

                    data[group2_id] = data2
                    self.group1_data[group1_id] = data

                    data = self.group2_data.get(group2_id, {})
                    data2 = data.get(group1_id, [])
                    for p in intersection:
                        data2.append(p)
                        # self._count()
                    data[group1_id] = data2
                    self.group2_data[group2_id] = data

            temp_count += 1

            if limit and temp_count >= limit:
                print "terminate early at limit", limit
                break

        print "Intersect: group_1: %d group_2: %d intersections: %d" % \
              (len(group1), len(group2), self._total_count)

    def get_intersections(self, group=1, id=None):
        if group == 1:
            return self.get_intersections_for_group1_id(id)
        else:
            return self.get_intersections_for_group2_id(id)

    def get_intersections_for_group1_id(self, group1_id):

        result = []
        data = self.group1_data.get(group1_id, {})

        for group2_id, polygons in data.iteritems():
            for p in polygons:
                result.append((p, group2_id))
        return result

    def get_intersections_for_group2_id(self, group2_id):

        result = []
        data = self.group2_data.get(group2_id, {})

        for group1_id, polygons in data.iteritems():
            for p in polygons:
                result.append((p, group1_id))
        return result

    def get_group1_ids(self):
        return [id for id in self.group1_data.iterkeys()]

    def get_group2_ids(self):
        return [id for id in self.group2_data.iterkeys()]
