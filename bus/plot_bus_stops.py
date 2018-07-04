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


class TempUtils(object):
    def __init__(self):
        self._postal_stops = {}
        self._postal_lines = {}


    def run_lines(self):
        """
         0 FID,
         1 Join_Count,
         2 TARGET_FID,
         3 JOIN_FID,
         4 full_name,
         5 dir_id,
         6 dir_name,
         7 pattern,
         8 line_id,
         9 line_name,
        10 map_id,
        11 map_name,
        12 url,
        13 km,
        14 hours_year,
        15 cost_year,
        16 vehicle_ty,
        17 vehicle_co,
        18 minheadway,
        19 maxheadway,
        20 minkph,
        21 maxkph,
        22 BUFF_DIST,
        23 ORIG_FID,
        24 Postal,
        25 Nhood,
        26 Nghd_Name
        """
        name = "../data/BRT_postal_lines.csv"

        f = open(name, "r")

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue
            line = line.strip()
            #print line
            parts = line.split(",")

            if len(parts) != 29:
                print line_count, len(parts)
                raise ValueError("badd")


            stop = parts[10] + parts[11]
            stop = stop.strip('"')
            postal = parts[26]
            hood = parts[28]

            if len(postal) != 7:
                # print "postal", postal
                if len(postal) == 0:
                    continue

                raise ValueError("bad postal code")

            if self._postal_lines.has_key(postal):
                # print "ignore duplicate postal"
                continue

            self._postal_lines[postal] = (stop, hood)
            # if line_count > 100:
            #     break

        f.close()

        #for k, v in self._postal_stops.iteritems():
        #    print k, v

        temp = [(k, v[1], v[0]) for k, v in self._postal_lines.iteritems()]
        temp = sorted(temp)
        #
        #
        print "index,postal_code,neighbourhood,line_name"
        for index, item in enumerate(temp):
             print "%d,%s,%s,%s" % (index, item[0], item[1], item[2])

    def run(self):
        """
         0 OBJECTID
         1 Join_Count
         2 TARGET_FID,
         3 JOIN_FID,
         4 map_id,
         5 map_name,
         6 stop_id,
         7 stop_name,
         8 lines,
         9 BUFF_DIST,
        10 ORIG_FID,
        11 Postal,
        12 Nhood,
        13 Nghd_Name,
        14 Shape_Length,
        15 Shape_Area

        0FID,
        1Join_Count,
        2TARGET_FID,
        3JOIN_FID,
        4map_id,
        5map_name,
        6stop_id,
        7stop_name,
        8lines,
        9BUFF_DIST,
        1ORIG_FID,
        2Postal,
        3Nhood,
        4Nghd_Name
        """
        name = "../data/BRT_postal_stops_2.csv"

        f = open(name, "r")

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue
            line = line.strip()
            #print line
            parts = line.split(",")

            # print len(parts)

            if len(parts) == 15:
                postal_index = 12
                nhood_index = 14

            else:
                postal_index = 12 + len(parts) - 15
                nhood_index = 14 + len(parts) - 15

            stop = parts[7]
            postal = parts[postal_index]
            hood = parts[nhood_index]

            if len(postal) != 7:
                # print "postal", postal
                if len(postal) == 0:
                    continue

                raise ValueError("bad postal code")

            if self._postal_stops.has_key(postal):
                # print "ignore duplicate postal"
                continue

            self._postal_stops[postal] = (stop, hood)
            # if line_count > 100:
            #     break

        f.close()

        #for k, v in self._postal_stops.iteritems():
        #    print k, v

        temp = [(k, v[1], v[0]) for k, v in self._postal_stops.iteritems()]
        temp = sorted(temp)


        print "index,postal_code,neighbourhood,stop_name"
        for index, item in enumerate(temp):
            print "%d,%s,%s,%s" % (index, item[0], item[1], item[2])

if __name__ == "__main__":

    # runner = Runner()
    # runner.plot()

    runner = TempUtils()
    runner.run()
    #runner.run_lines()


    # runner.plot_route()
    # runner.make_stop_csv_file()




