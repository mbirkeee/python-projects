import shapefile

from my_utils import TransitData

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2
from map_html import CIRCLE_RED_20

class Runner(object):

    def __init__(self):
        self._transit_data = TransitData()
        self._transit_data.load_stops_from_csv("../data/sts/csv/2018_05_04/my-TransitStops.csv")


    def make_da_csv_file(self):



        sf = shapefile.Reader("../data/shapefiles/DA_centriods/Da_CentroidPoints.dbf")
        records = sf.records()
        print "len(records)", len(records)

        for item in records:
            # print item
            # print dir(item)
            #print item.shapeType
            pass

        shapes = sf.shapes()
        print len(shapes)

        for shape in shapes:
            print shape
            print repr(shape)
            print dir(shape)
            print shape.points
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

    def run(self):
        print "run called"

        map_name = "./data/maps/bus_stops.html"

        f = open(map_name, "w")
        f.write(MAP_TOP)
        f.write("var circle = {\n")

        i = 0
        stops = self._transit_data.get_stops()
        for value in stops.itervalues():
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
    # runner.run()
    runner.make_da_csv_file()




