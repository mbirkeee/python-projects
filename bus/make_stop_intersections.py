import argparse
import shapefile

from da_manager import DaData
from data_manager import dataman_factory
from intersect import Intersect
from modes import BUFFER_METHOD

from geometry import Point
from geometry import Polygon

class BufferManager(object):

    def __init__(self, buffer_method=None, dataset=None):

        self._data = None

        self._buffer_method = buffer_method
        self._dataset = dataset

    def set_buffer_method(self, buffer_method):
        self._buffer_method = buffer_method

    def set_dataset(self, dataset):
        self._dataset = dataset

    def get_buffer(self, stop_id):

        if self._data is None:
            self.load_shapefile()

        buffer_p = self._data.get(stop_id)
        if buffer_p is None:
            raise ValueError("No buffer for stop ID: %s" % repr(stop_id))

        print "Buffer manager got buffer from stop: %d" % stop_id
        return buffer_p

    def load_shapefile(self):

        if self._buffer_method == BUFFER_METHOD.NETWORK_400:
            file_name = "data/shapefiles/stop_buffers/%s_network_400.shp" % (self._dataset)
        elif self._buffer_method == BUFFER_METHOD.NETWORK_532:
            file_name = "data/shapefiles/stop_buffers/%s_network_532.shp" % (self._dataset)
        elif self._buffer_method == BUFFER_METHOD.NETWORK_2000:
            file_name = "data/shapefiles/stop_buffers/%s_network_2000.shp" % (self._dataset)
        else:
            raise ValueError("buffer method not supported: %s" % self._buffer_method)

        print "Want to load shapefile: %s" % file_name

        self._data = {}
        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        print "number of records:", len(records)

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        for i, record in enumerate(records):
            # print repr(record)
            stop_id = record[2]
            # print "stop_id", stop_id, type(stop_id)
            parts = stop_id.split(" ")
            s = parts[0].strip()
            # print "here", s, type(s)
            stop_id = int(s)
            # print stop_id

            shape = shapes[i]

            # print repr(shape)

            polygon = Polygon()

            # print stop_id, len(shape.points)
            if len(shape.points) < 4:
                raise ValueError("not enough points!!!")

            # test_id = 3032
            test_id = 99999999

            if stop_id == test_id:
                for index, point in enumerate(shape.points):
                    print index, point[0], point[1], type(point[0]), type(point[1])

            start_point = None
            for index in xrange(len(shape.points)):
                item = shape.points[index]
                if start_point is None:
                    start_point = (item[0], item[1])
                else:
                    if item[0] == start_point[0] and item[1] == start_point[1]:
                        break
                polygon.add_point(Point(item[0], item[1]))

            # for index in xrange(len(shape.points)-1):
            #     item = shape.points[index]
            #     polygon.add_point(Point(item[0], item[1]))

            self._data[stop_id] = polygon
            print "shape polygon area", polygon.get_area()

            if len(shape.parts) > 1:
                print "Stop ID", stop_id, "parts", len(shape.parts)

            if stop_id == test_id:
                print dir(shape)
                print repr(shape.parts)
                print repr(shape.shapeType)
                raise ValueError("temp stop")




class Runner(object):

    def __init__(self, args):

        self._buffer_method = args.buffer_method
        self._dataset = args.dataset

        self._daman = DaData()
        self._dataman = dataman_factory(self._dataset, link_route_shapes=False, link_stops=False)

        self._buffer_man = None
        if self._buffer_method == BUFFER_METHOD.NETWORK_400:
            # The buffer manager is used to get externally computed buffers (e.g, network buffers from ArcGIS
            self._buffer_man = BufferManager(self._buffer_method, self._dataset)

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
                # The stop needs to know the dataset for cases where the buffer is read from
                # a file (e.g., ArcGIS computed network buffers)
                stop.make_buffer(self._buffer_method, buffer_manager=self._buffer_man)

            intersect.process(all_stops, das)
            intersect.to_shapefile(self._buffer_method, self._dataset, all_stops)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Make Stop Intersections')
    parser.add_argument("-d", "--dataset", help="Dataset", type=str, required=True)
    parser.add_argument("-b", "--buffer_method", help="Stop buffer method", required=True, type=str)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()
