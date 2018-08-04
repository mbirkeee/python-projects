import os
import math

from geometry import Point
from geometry import Polygon

class Stops(object):

    def __init__(self, base_path):

        self._base_path = base_path
        self._data = {}
        self.read_file()

    def read_file(self):
        """
        0 stop_id,
        1 stop_code,
        2 stop_lat,
        3 stop_lon,
        4 location_type,
        5 wheelchair_boarding,
        6 name
        """

        file_name = os.path.join(self._base_path, "my-TransitStops.csv")

        result = {}
        line_count = 0
        f = None
        fake_stop_id = 10000

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                parts = line.split(",")

                try:
                    stop_id = int(parts[1].strip())

                except Exception as err:
                    print "Exception processing line: %s" % repr(err)
                    print "line: %s" % line
                    stop_id = fake_stop_id
                    print "Assign fake stop ID: %d" % fake_stop_id
                    fake_stop_id += 1

                try:
                    name = parts[6].strip()
                    lat = float(parts[2].strip())
                    lng = float(parts[3].strip())

                    # print stop_id, lat, lng, name

                    stop_data = {
                        'point' : Point(lat, lng),
                        'name'  : name
                    }

                    result[stop_id] = stop_data

                except Exception as err:
                    print "Exception processing line: %s" % repr(err)
                    print "line: %s" % line


        finally:
            if f: f.close()

        self._data = result

    def get_name(self, stop_id):
        # print "Getting STOP name for stop id", stop_id

        stop_data = self._data.get(stop_id)
        if stop_data is None:
            return None

        return stop_data.get('name')

    def get_point(self, stop_id):

        stop_data = self._data.get(stop_id)
        if stop_data is None:
            return None

        return stop_data.get('point')

    def get_ids(self):
        result = [stop_id for stop_id in self._data.iterkeys()]
        return result

    def get_buffer(self, stop_id):

        stop_data = self._data.get(stop_id)
        if stop_data is None:
            return None

        return stop_data.get('buffer')

    def make_round_buffer(self, size):

        for stop_id, stop_data in self._data.iteritems():
            print "Making buffer for stop_id: %d" % stop_id
            point = stop_data.get('point')
            # print repr(point)
            x = point.get_x()
            y = point.get_y()

            p = Polygon()
            for i in xrange(360/10):
                r = math.radians(i * 10)
                p.add_point(Point(x + size * math.sin(r), y + size * math.cos(r)))

            stop_data['buffer'] = p

    def make_square_buffers(self, size):

        half = float(size)/2.0
        corners = [
            (-half,  half),
            ( half,  half),
            ( half, -half),
            (-half, -half),
        ]

        for stop_id, stop_data in self._data.iteritems():
            print "Making buffer for stop_id: %d" % stop_id
            point = stop_data.get('point')
            # print repr(point)
            p = Polygon()
            for corner in corners:
                p.add_point(Point(point.get_x() + corner[0], point.get_y() + corner[1]))

            stop_data['buffer'] = p
