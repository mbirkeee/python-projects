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
        self._da_pop = {}


    def run_lines(self):
        """
         0 FID,              FID,
         1 Join_Count,       Join_Count,
         2 TARGET_FID,       TARGET_FID,
         3 JOIN_FID,         JOIN_FID,
         4 full_name,        full_name,
         5 dir_id,           dir_id,
         6 dir_name,         dir_name,
         7 pattern,          pattern,
         8 line_id,          line_id,
         9 line_name,        line_name,
        10 map_id,           map_id,
        11 map_name,         map_name,
        12 url,              url,
        13 km,               km,
        14 hours_year,       hours_year,
        15 cost_year,        cost_year,
        16 vehicle_ty,       vehicle_ty,
        17 vehicle_co,       vehicle_co,
        18 minheadway,       minheadway,
        19 maxheadway,       maxheadway,
        20 minkph,           minkph,
        21 maxkph,           maxkph,
        22 BUFF_DIST,        BUFF_DIST,
        23 ORIG_FID,         ORIG_FID,
        24 Postal,           Postal,
        25 Nhood,            Nhood,
        26 Nghd_Name         Nghd_Name
        """
        name = "../data/BRT_postal_lines_800.csv"

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
                raise ValueError("badd: %d" % len(parts))


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

    def run_pop(self):
        """

        """
        name = "../data/BRT_pop_lines_800.csv"

        f = open(name, "r")

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue
            line = line.strip()
            #print line
            parts = line.split(",")

            # print "LEN PARTS!!!!", len(parts)
            if len(parts) != 84:
                print line_count, len(parts)
                raise ValueError("badd: %d" % len(parts))

            pop = int(parts[81].strip())
            under15 = int(parts[83].strip())
            da_id = parts[82].strip()
            pcent_bus = int(parts[77].strip())
            #print da_id, pop, under15, pcent_bus

            # hood = parts[28]
            #
            # if len(postal) != 7:
            #     # print "postal", postal
            #     if len(postal) == 0:
            #         continue
            #
            #     raise ValueError("bad postal code")
            #
            if self._da_pop.has_key(da_id):
                # print "ignore duplicate da_id"
                continue

            self._da_pop[da_id] = (pop, under15, pop-under15, pcent_bus)
            # if line_count > 100:
            #     break

        f.close()

        #for k, v in self._postal_stops.iteritems():
        #    print k, v

        temp = [(k, v[0], v[1], v[2], v[3]) for k, v in self._da_pop.iteritems()]
        temp = sorted(temp)
        #
        #
        print "index,da_id,pop,pop_under_15,pop_15_and_over,percent_bus_riders"
        for index, item in enumerate(temp):
             print "%d,%s,%d,%d,%d,%d" % (index, item[0], item[1], item[2], item[3], item[4])

    def run_pop_2018_07_08(self):


        cols = """
        OBJECTID,Join_Count,TARGET_FID,JOIN_FID,lda_000a16a_e_DAUID,lda_000a16a_e_PRUID,
        lda_000a16a_e_PRNAME,lda_000a16a_e_CDUID,lda_000a16a_e_CDNAME,lda_000a16a_e_CDTYPE,
        lda_000a16a_e_CCSUID,lda_000a16a_e_CCSNAME,lda_000a16a_e_CSDUID,lda_000a16a_e_CSDNAME,
        lda_000a16a_e_CSDTYPE,lda_000a16a_e_ERUID,lda_000a16a_e_ERNAME,lda_000a16a_e_SACCODE,
        lda_000a16a_e_SACTYPE,lda_000a16a_e_CMAUID,lda_000a16a_e_CMAPUID,lda_000a16a_e_CMANAME,
        lda_000a16a_e_CMATYPE,lda_000a16a_e_CTUID,lda_000a16a_e_CTNAME,lda_000a16a_e_ADAUID,
        busridershipperDA_csv_FID,busridershipperDA_csv_DAUID,busridershipperDA_csv_PRUID,
        busridershipperDA_csv_PRNAME,busridershipperDA_csv_CDUID,busridershipperDA_csv_CDNAME,
        busridershipperDA_csv_CDTYPE,busridershipperDA_csv_CCSUID,busridershipperDA_csv_CCSNAME,
        busridershipperDA_csv_CSDUID,busridershipperDA_csv_CSDNAME,busridershipperDA_csv_CSDTYPE,
        busridershipperDA_csv_ERUID,busridershipperDA_csv_ERNAME,busridershipperDA_csv_SACCODE,
        busridershipperDA_csv_SACTYPE,busridershipperDA_csv_CMAUID,busridershipperDA_csv_CMAPUID,
        busridershipperDA_csv_CMANAME,busridershipperDA_csv_CMATYPE,busridershipperDA_csv_CTUID,
        busridershipperDA_csv_CTNAME,busridershipperDA_csv_ADAUID,busridershipperDA_csv_da_population_csv_FID,
        busridershipperDA_csv_DAUID_1,busridershipperDA_csv_da_feature_id,busridershipperDA_csv_population,
        busridershipperDA_csv_GEOUID,busridershipperDA_csv_FID_1,busridershipperDA_csv_PBTRAN,
        da_population_csv_FID,da_population_csv_DAUID,da_population_csv_da_feature_id,
        da_population_csv_population,under15saskdapop_csv_DAUID,under15saskdapop_csv_UNDERFIFT,
        Shape_Length,Shape_Area
        """

        columns = cols.split(",")
        # print "len(col)", len(columns)

        name = "../data/BRT_stops_800_da_2018_07_08.csv"

        # raise ValueError("tmep stop")

        f = open(name, "r")

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue
            line = line.strip()
            #print line
            parts = line.split(",")

            # print "LEN PARTS!!!!", len(parts)
            if len(parts) != 64:
                print line_count, len(parts)
                raise ValueError("badd: %d" % len(parts))

            try:
                pop = int(parts[59].strip())
            except:
                print "bad pop", parts[59]
                continue

            try:
                under15 = int(parts[61].strip())
            except:
                continue

                # print "bad u15", parts[61]
                under15 = 0

            da_id = parts[60].strip()

            try:
                pcent_bus = int(parts[55].strip())
            except:
                continue

                #print "bad pcent", parts[55]

            # print pop, da_id, under15, pcent_bus

            if self._da_pop.has_key(da_id):
                # print "ignore duplicate da_id"
                continue

            self._da_pop[da_id] = (pop, under15, pop-under15, pcent_bus)
            # if line_count > 100:
            #     break

        f.close()

        #for k, v in self._postal_stops.iteritems():
        #    print k, v

        temp = [(k, v[0], v[1], v[2], v[3]) for k, v in self._da_pop.iteritems()]
        temp = sorted(temp)
        #
        #
        print "index,da_id,pop,pop_under_15,pop_over_15,percent_bus_riders_over_15,total_bus_riders_over_15"
        for index, item in enumerate(temp):
            total_bus_riders = int(float(item[3] * item[4])/100.0)
            print "%d,%s,%d,%d,%d,%d,%d" % (index, item[0], item[1], item[2], item[3], item[4],total_bus_riders)

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

            stop_id = parts[6]
            stop_name = parts[7]
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

            self._postal_stops[postal] = (hood, stop_id, stop_name)
            # if line_count > 100:
            #     break

        f.close()

        #for k, v in self._postal_stops.iteritems():
        #    print k, v

        temp = [(k, v[0], v[1], v[2]) for k, v in self._postal_stops.iteritems()]
        temp = sorted(temp)


        print "index,postal_code,neighbourhood,stop_id,stop_name"
        for index, item in enumerate(temp):
            print "%d,%s,%s,%s,%s" % (index, item[0], item[1], item[2], item[3])

    def da_pop_july_12(self):

        name = "../data/DaandPostalCodes.csv"

        f = open(name, "r")

        print "index,postal_code,da_id"
        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue
            line = line.strip()
            # print line

            parts = line.split(",")
            # print parts[4]
            # print parts[62]

            print "%d,%s,%s" % (line_count-1, parts[62], parts[4])
        f.close()

    def run_2018_07_08(self):
        """
         0 OBJECTID,
         1 Join_Count,
         2 TARGET_FID,
         3 JOIN_FID,
         4 index,
         5 stop_id,
         6 stop_name,
         7 lat,
         8 lng,
         9 on_red,
        10 on_green,
        11 on_blue,
        12 BUFF_DIST,
        13 ORIG_FID,
        14 Postal,
        15 Nhood,
        16 Nghd_Name,
        17 Shape_Length,
        18 Shape_Area
        """
        name = "../data/BRT_stops_800_2018_07_08.csv"

        f = open(name, "r")

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue
            line = line.strip()
            #print line
            parts = line.split(",")

            # print len(parts)

            if len(parts) != 19:
                print line
                raise ValueError("Wrong number of parts")

            postal_index = 14
            nhood_index = 16

            stop_name = parts[6]
            stop_id = parts[5]

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

            self._postal_stops[postal] = (hood, stop_id, stop_name)
            # if line_count > 100:
            #     break

        f.close()

        #for k, v in self._postal_stops.iteritems():
        #    print k, v

        temp = [(k, v[0], v[1], v[2]) for k, v in self._postal_stops.iteritems()]
        temp = sorted(temp)


        print "index,postal_code,neighbourhood,stop_id,stop_name"
        for index, item in enumerate(temp):
            print "%d,%s,%s,%s,%s" % (index, item[0], item[1], item[3], item[2])


if __name__ == "__main__":

    # runner = Runner()
    # runner.plot()

    runner = TempUtils()
    # runner.run()
    # runner.run_lines()
    # runner.run_2018_07_08()
    # runner.run_pop_2018_07_08()

    runner.da_pop_july_12()
    # runner.plot_route()
    # runner.make_stop_csv_file()




