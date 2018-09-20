from my_utils import TransitData
from stop_times import StopTimes
from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2
from map_html import CIRCLE_RED_20
from map_html import MARKER

class Runner(object):

    def __init__(self):
        # self._transit_data = TransitData()
        # self._transit_data.load_stops_from_csv("../data/sts/csv/2018_05_04/my-TransitStops.csv")

        self._base_path = "../data/sts/csv/2018_05_04/"

        # self._service_type = SERVICE.MWF
        # self._time_of_day = 8 * 60 * 60  # 8 AM

        # self._weight = Weight()
        # self._intersect = Intersect()
        self._stop_times = StopTimes(self._base_path)


    def make_stop_csv_file(self):


        f = open("my_transit_stops.csv", "w")
        f.write("index,stop_id,utm_x,utm_y\n")

        stops = self._transit_data.get_stops()

        index = 1
        for key, value in stops.iteritems():
            print key
            print value
            x = value.get('x')
            y = value.get('y')

            f.write("%s,%d,%f,%f\n" % (index, key, x, y))
            index += 1

        f.close()

    def plot(self):

        map_name = "./data/maps/bus_stops.html"

        f = open(map_name, "w")
        f.write(MAP_TOP)
        f.write("var circle = {\n")

        i = 0
        stop_ids = self._stop_times.get_stop_ids()

        for stop_id in stop_ids:
            print "Adding stop", stop_id
            lat, lon = self._stop_times.get_stop_lat_lon(stop_id)
            f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))
            i += 1
            if i > 10: break

        f.write("};\n")
        f.write(CIRCLE_RED_20)

        i = 0
        test = [4343, 3787, 4081]
        f.write("var marker = {\n")

        for stop_id in test:
            stop_label = "%s" % stop_id
            stop_title = "%s" % self._stop_times.get_stop_name(stop_id)
            lat, lon = self._stop_times.get_stop_lat_lon(stop_id)
            f.write("%d:{center:{lat:%f,lng:%f},title:'%s',label:'%s',},\n" % (i, lat, lon, stop_title, stop_label))
            i += 1

        f.write("};\n")
        f.write(MARKER)

        f.write(MAP_BOTTOM)
        f.close()


if __name__ == "__main__":

    runner = Runner()
    runner.plot()
