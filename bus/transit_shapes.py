import os
from geometry import Point
from geometry import Polyline

from route_id_names import BAD_SHAPES

class TransitShapes(object):

    def __init__(self, base_path):

        self._base_path = base_path
        self._data = {}
        self.read_file()
        self.sort_data()

    def sort_data(self):

        result = {}

        for shape_id, points in self._data.iteritems():
            result[shape_id] = sorted(points)

#        for shape_id, points in result.iteritems():
#            # print "shape_id", shape_id
#            for item in points:
#                print item

            #print "shape_id", shape_id, "points", points

        self._data = result

        #raise ValueError('temp stop')

    def read_file(self):
        """
        0 shape_id,
        1 shape_lat,
        2 shape_lon,
        3 point_seq,
        4 dist
        """
        file_name = os.path.join(self._base_path, "my-TransitShapes.csv")

        print "Reading file: %s..." % file_name
        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                #print parts

                shape_id = int(parts[0].strip())
                lat = float(parts[1].strip())
                lng = float(parts[2].strip())
                seq = int(parts[3].strip())

                points = self._data.get(shape_id, [])
                points.append((seq, Point(lat, lng)))
                self._data[shape_id] = points

            # raise ValueError("temp stop")

        finally:
            if f:
                f.close()

        print "Read %d shapes from %s" % (line_count-1, file_name)

    def get_polyline(self, shape_id):

        point_data = self._data.get(shape_id)
        if point_data is None:
            raise ValueError("No data for shape id: %s" % repr(shape_id))
        p = Polyline()
        for item in point_data:
            p.add_point(item[1])
        return p

    def get_points(self, shape_id_list):

        result = []
        if not isinstance(shape_id_list, list):
            shape_id_list = [shape_id_list]

        print "---"
        for shape_id in shape_id_list:
            point_data = self._data.get(shape_id)
            if point_data is None:
                raise ValueError("No data for shape id: %s" % repr(shape_id))

            # for point in point_data:
            #     print point

            print "Shape ID: %d Adding %d points" % (shape_id, len(point_data))
            result.extend(point_data)

        # s = sorted(result)

        points = [item[1] for item in result]
        return points
