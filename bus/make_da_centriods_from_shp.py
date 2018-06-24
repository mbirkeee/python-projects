import shapefile
import pyproj

from my_utils import TransitData

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2
from map_html import CIRCLE_RED_20


class Runner(object):

    def __init__(self):
        self._transit_data = TransitData()
        self._transit_data.load_stops_from_csv("../data/sts/csv/2018_05_04/my-TransitStops.csv")

        self._myproj = pyproj.Proj("+init=EPSG:32613")

        self._data_pop_by_da = {}
        self._centroids = {}

    def load_stats_can_pop_data(self):

        f = open("../data/2016_pop.csv", "r")

        expected_parts = 15

        for line in f:
            # print "LINE", line.strip()
            parts = line.split(",")
            # print len(parts)

            if len(parts) != 15:
                print "BAD LINE!!!!!", line
                print len(parts)
                continue

            try:
                da_id = int(parts[1].strip('"'))
                pop = int(parts[12].strip('"'))
            except Exception as err:
                print "Failed for line:", line
                continue
                # raise ValueError("unexpected number of parts")

            print "ID:", da_id, "POP:", pop

            if self._data_pop_by_da.has_key(da_id):
                raise ValueError("Already have da_id: %s" % da_id)

            self._data_pop_by_da[da_id] = pop

        f.close()

    def make_da_csv_file(self):

        sf = shapefile.Reader("../data/shapefiles/DA_centriods/Da_CentroidPoints.dbf")
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len recoreds != len shapes")

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        f = open("da_centriods.csv", "w")
        f.write("index,da_id,da_feature_id,X,utm_x,utm_y,population\n")

        for i in xrange(len(records)):
            record = records[i]
            shape = shapes[i]

            print repr(record)

            print shape.points

            point = shape.points[0]

            da_id = int(record[0])
            da_fid = int(record[22])
            x = point[0]
            y = point[1]

            population = self._data_pop_by_da.get(da_id)
            if population is None:
                raise ValueError("Failed tpo get pop for %s" % repr(da_id))

            line =  "%d,%d,%d,%f,%f,%d" % (i, da_id, da_fid, x, y, population)
            f.write("%s\n" % line)

            lon, lat =  self._myproj(x, y, inverse=True)

            self._centroids[da_id] = {
                'x' : x,
                'y' : y,
                'lat' : lat,
                'lon' : lon
            }

        f.close()
            # if i > 10: break


        # f = open("my_transit_stops.csv", "w")
        # f.write("index,stop_id,utm_x,utm_y\n")
        #
        # stops = self._transit_data.get_stops()
        #
        # index = 1
        # for key, value in stops.iteritems():
        #     print key
        #     print value
        #     x = value.get('x')
        #     y = value.get('y')
        #
        #     f.write("%s,%d,%f,%f\n" % (index, key, x, y))
        #     index += 1
        #
        # f.close()

    def plot(self):

        map_name = "data/maps/da_centroids.html"

        f = open(map_name, "w")

        f.write(MAP_TOP)
        f.write("var circle = {\n")

        i = 0
        for value in self._centroids.itervalues():
            lat = value.get('lat')
            lon = value.get('lon')
            f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))
            i += 1

        f.write("};\n")
        f.write(CIRCLE_RED_20)
        f.write(MAP_BOTTOM)
        f.close()


if __name__ == "__main__":

    runner = Runner()
    # runner.plot()
    runner.load_stats_can_pop_data()
    runner.make_da_csv_file()
    # runner.plot()



