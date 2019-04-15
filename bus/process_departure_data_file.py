import datetime
import math

from data_manager import dataman_factory
from da_manager import DaData

from dataset import DATASET

class Runner(object):

    def __init__(self):

        self._dataman = None
        self._daman = None
        self._dataset = None

        self._valid_stop_ids = []
        self._valid_route_ids = []

        self._invalid_stop_dict = {}
        self._valid_stop_dict = {}

        self._stop_to_da_map = {}

        self._da_departures = {}
        self._da_stop_count = {}
        self._taps_per_route_dict = {}
        self._taps_per_date_dict = {}
        self._taps_per_day_dict = {}

        self._keep_iso_days = [1,2,3,4,5] # Monday - Friday

        self._iosday = ["Invalid", "Monday", "Tuesday", "Wednesday",
                        "Thursday", "Friday", "Saturday", "Sunday"]

    def make_valid_stop_list(self):

        routes = self._dataman.get_routes()
        for route in routes:
            route_number = route.get_number()
            self._valid_route_ids.append(route_number)

        stops = self._dataman.get_active_stops()

        das = self._daman.get_das()

        print "Mapping stops to DAs"

        for stop in stops:
            # print type(stop)
            point = stop.get_point()

            # print point
            stop_id = stop.get_id()
            #print stop_id, type(stop_id)

            self._valid_stop_ids.append(stop_id)

            match_count = 0
            for da in das:
                polygon = da.get_polygon()

                if point.within(polygon):
                    match_count += 1
                    self._stop_to_da_map[stop_id] = da
                    break


            if match_count == 0:
                print "FAILED TO MATCH POINT TO DA"

            elif match_count == 1:
                # print "MATCHED POINT TO POLYGON!!!!"
                pass

            else:
                print "bad match count !!!!!"

        print "Finished mapping stops to DAs"


        for stop, da in self._stop_to_da_map.iteritems():
            da_id = da.get_id()
#             print stop, da_id
            c = self._da_stop_count.get(da_id, 0)
            c += 1
            self._da_stop_count[da_id] = c

#         for da, stop_count in self._da_stop_count.iteritems():
#             print da_id, stop_count

        # print "there are %d stops", len(self._stop_to_da_map)

        # raise ValueError('temp stop')

        # print self._valid_stop_ids

    def get_filter_stops(self):

        filter_stops =[
            5904, # TAPS: 3264 NAME: Place Riel / Terminal E&S
            5903, # TAPS: 993 NAME: Place Riel / Terminal W&N
            5902, # TAPS: 800 NAME: Downtown Terminal East
            5901, # TAPS: 749 NAME: Downtown Terminal West
            5899, # TAPS: 874 NAME: Downtown Terminal North
            5900, # TAPS: 619 NAME: Downtown Terminal South
            5910, # TAPS: 444 NAME: Centre Mall Terminal I/B
            5897, # TAPS: 416 NAME: 3rd Avenue / 23rd Street
            5906, # TAPS: 395 NAME: Market Mall Terminal I/B
            5912, # TAPS: 364 NAME: Confederation Terminal
            4174, # TAPS: 358 NAME: Superstore
            5908, # TAPS: 337 NAME: Lawson Terminal I/B
        ]

        return filter_stops
        """
        if self._dataset == DATASET.JUNE:

        else:
            filter_stops = [
                5904, # TAPS: 5689 NAME: Place Riel / Terminal E&S
                5903, # TAPS: 2494 NAME: Place Riel / Terminal W&N
                5912, # TAPS: 1258 NAME: Confederation Terminal
                5908, # TAPS: 1055 NAME: Lawson Terminal I/B
                4174, # TAPS: 927 NAME: Superstore
            # #    4345, # TAPS: 879 NAME: Hunter / Vic
            #     5910, # TAPS: 877 NAME: Centre Mall Terminal I/B
                5899, # TAPS: 874 NAME: Downtown Terminal North
            # #    3173, # TAPS: 850 NAME: 25th Street / 5th Avenue
            # #    5556, # TAPS: 833 NAME: 8th Street / JYSK Store
            # #    3629, # TAPS: 741 NAME: McKercher / Tait Crescent
            # #    5897, # TAPS: 738 NAME: 3rd Avenue / 23rd Street
            # #    3343, # TAPS: 731 NAME: 8th Street / McKercher
            #     5906, # TAPS: 715 NAME: Market Mall Terminal I/B
                5901, # TAPS: 694 NAME: Downtown Terminal West
            # #    3585, # TAPS: 646 NAME: Steeves / John A MacDonald
            #     5900, # TAPS: 619 NAME: Downtown Terminal South
            # #    4172, # TAPS: 608 NAME: 8th Street / Arlington
            # #    3170, # TAPS: 604 NAME: 25th Street / 3rd Avenue
            # #    4315, # TAPS: 576 NAME: Idylwyld / 33rd Street
            #     5909, # TAPS: 554 NAME: Centre Mall Terminal O/B
            # #    4095, # TAPS: 551 NAME: Central / 115th Street
            # #    3015, # TAPS: 550 NAME: Forest / 500-Block
            # #    3007, # TAPS: 525 NAME: 108th Street / Egbert
            # #    3605, # TAPS: 500 NAME: 8th Street / Chaben
            #     5911, # TAPS: 487 NAME: Confederation Terminal
            # #    3128, # TAPS: 479 NAME: 22nd Street / Avenue P
            # #    5888, # TAPS: 463 NAME: Kenderdine / Kerr
            #     5413, # TAPS: 462 NAME: Downtown Terminal West1
            # #    3823, # TAPS: 462 NAME: McKercher / Heritage
            # #    5482, # TAPS: 461 NAME: Stonebridge / Galloway
            # #    5902, # TAPS: 454 NAME: Downtown Terminal East
        ]

        return filter_stops
        """

    def run(self, filename):

        if filename.find('jan') > 0:
            self._dataset = DATASET.JUNE
        else:
            self._dataset = DATASET.JULY

        self._dataman = dataman_factory(self._dataset)
        self._daman = DaData()

        runner.make_valid_stop_list()
        filter_stops = self.get_filter_stops()

        expected_cols = None
        zero_count = 0
        stop_count = 0
        bad_count = 0
        bad_route_count = 0
        transfer_count = 0
        wrong_time_count = 0
        wrong_day_count = 0
        filter_count = 0

        valid_count = 0
        invalid_count = 0

        f = open(filename)

        count = 0
        for line in f:
            count += 1
            # print line

            parts = line.split(",")
            col_count = len(parts)

            if expected_cols is None:
                expected_cols = col_count
            else:

                if col_count != expected_cols:
                    raise ValueError("bad parts count")

            if count == 1:
                print parts
                continue

            info = parts[8].strip()

            # Skip transfers all transfers
            if info.find('ansfer') > 0:
                transfer_count += 1
                print "SKIPPING TRANSFER"
                continue

            route = int(parts[4])

            if route not in self._valid_route_ids:
                bad_route_count += 1
                # print "SKIPPING BAD ROUTE", bad_route_count
                continue

            route_data = self._taps_per_route_dict.get(route, {})

            tap_count = route_data.get('tap_count', 0)
            tap_count += 1
            tap_count_err = route_data.get('err_count', 0)

            # print "ROUTE", route

            stop = int(parts[5])

            bad_stop = False
            if stop == 0:
                zero_count += 1
                bad_stop = True

            if stop == 9999:
                bad_count += 1
                bad_stop = True

            if bad_stop:
                tap_count_err += 1

            route_data['tap_count'] = tap_count
            route_data['err_count'] = tap_count_err
            self._taps_per_route_dict[route] = route_data

            if bad_stop:
                continue

            if stop in filter_stops:
                filter_count += 1
                continue

            # Examine the date
            date = parts[2]

            c = self._taps_per_date_dict.get(date, 0)
            c += 1
            self._taps_per_date_dict[date] = c

            # print date

            date_object = self.get_date_object(date)
            isoweekday = date_object.isoweekday()
            day = self._iosday[isoweekday]

            c = self._taps_per_day_dict.get(day, 0)
            c += 1
            self._taps_per_day_dict[day] = c

            if isoweekday not in self._keep_iso_days:
                wrong_day_count += 1
                print "SKIP INVALID DAY", wrong_day_count
                continue

            # Examine the time
            t = parts[3]
            t_parts = t.split(":")
            h = int(t_parts[0])
            m = int(t_parts[1])
            minutes = 60 * h + m
#            print "TIME", h, m, minutes

            if minutes < 6*60 or minutes > 9*60:
                wrong_time_count += 1
                print "SKIP INVALID TIME!!!!", wrong_time_count
                continue

            stop_count += 1

            try:
                bus_pass = int(parts[6].strip())
            except:
                bus_pass = None

            # print "BUS PASS NO", bus_pass

            if bus_pass is None:
                # print "SKIP NO BAS PASS"
                continue

            if stop in self._valid_stop_ids:
                valid_count += 1

                # Add count to DA
                da = self._stop_to_da_map.get(stop)
                da_id = da.get_id()

                # c = self._da_departures.get(da_id, 0)
                # c += 1
                # self._da_departures[da_id] = c

                user_list = self._da_departures.get(da_id, [])
                user_list.append(bus_pass)
                self._da_departures[da_id] = user_list

                # Add count to stop
                c = self._valid_stop_dict.get(stop, 0)
                c += 1
                self._valid_stop_dict[stop] = c

            else:
                invalid_count += 1

                x = self._invalid_stop_dict.get(stop, 0)
                x += 1
                self._invalid_stop_dict[stop] = x

        f.close()


        print "Read %d lines" % count

        print "zero count:", zero_count
        print "bad stop (e.g., 9999) count:", bad_count
        print "transfer count", transfer_count
        print "wrong time count", wrong_time_count
        print "wrong day count", wrong_day_count
        print "bad_route_count", bad_route_count
        print "filter count", filter_count
        print "stop count", stop_count, valid_count, invalid_count

        print "Invalid Stops:"
        print "--------------"
        for stop, count in self._invalid_stop_dict.iteritems():
            print "Stop: %d: %d" % (stop, count)

        if self._dataset == DATASET.JUNE:
            month = "jan"
        else:
            month = "sept"

        f_out  = open("%s_taps_per_pop.csv" % month, "w")
        f2_out = open("%s_taps_per_stop.csv" % month, "w")
        f3_out = open("%s_user_percentage.csv" % month, "w")

        for da_id, depart_users in self._da_departures.iteritems():
            depart_count = len(depart_users)
            unique_users = len(list(set(depart_users)))
            print "DA %d DEPARTS: %d USERS: %d" % (da_id, depart_count, unique_users)

            da = self._daman.get_da(da_id)
            population = da.get_population()

            taps_per_pop = float(depart_count)/float(population)
            taps_per_stop = float(depart_count)/float(self._da_stop_count.get(da_id))
            user_percentage = 100.0 * ( float(unique_users) / float(population))

            # if user_percentage > 20.0:
            #      print "CAPPING USER PERCENTAGE AT 10 for DA: ", da_id
            #      user_percentage = 20.0
            # user_percentage = math.log(user_percentage, 10)

            # taps_per_stop = math.log10(taps_per_stop)
            # taps_per_pop = math.log10(taps_per_pop)

            f_out.write("%d,%f\n" % (da_id, taps_per_pop))
            f2_out.write("%d,%f\n" % (da_id, taps_per_stop))
            f3_out.write("%d,%f\n" % (da_id, user_percentage))

        f_out.close()
        f2_out.close()
        f3_out.close()

    def get_date_object(self, date_str):
        if self._dataset == DATASET.JULY:
            date_object = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date_object = datetime.datetime.strptime(date_str, "%m/%d/%Y")

        return date_object

    def display_date_data(self):

        items = []
        for date, taps in self._taps_per_date_dict.iteritems():
            items.append((date, taps))

        items.sort()
        for item in items:
            date = item[0]
            taps = item[1]
            date_object = self.get_date_object(date)
            day = self._iosday[date_object.isoweekday()]
            print "%10s %10s  %8d" % (date, day, taps)

        print "\n\n\n"

        items = []
        for day, taps in self._taps_per_day_dict.iteritems():
            items.append((taps, day))

        items.sort()
        items.reverse()

        for item in items:
            taps = item[0]
            day = item[1]
            print "%12s  %8d" % (day, taps)

    def display_route_data(self):

        if self._dataman is None:
            self._dataman = dataman_factory(self._dataset)

        route_number_name_map = {}
        taps_per_route = {}

        route_list = self._dataman.get_routes()
        for item in route_list:
            print "this is a route", item

            route_number = item.get_number()
            route_name = item.get_name()
            route_number_name_map[route_number] = route_name
            taps_per_route[route_number] = 0

        temp_list = []
        for route, data in self._taps_per_route_dict.iteritems():
            taps = data.get('tap_count', 0)
            errors = data.get('err_count', 0)
            name = route_number_name_map.get(route, "UNKNOWN")
            temp_list.append((taps, errors, route, name))

            # Add to taps per route *if route exists!*
            if taps_per_route.has_key(route):
                taps_per_route[route] = taps

        temp_list.sort()
        temp_list.reverse()

        for item in temp_list:
            taps = item[0]
            errors = item[1]
            route = item[2]
            name = item[3]

            error_percent = 100.0 * errors / taps

            print "ROUTE: %5d %-30s  taps: %5d errors: %5d (percent: %3.2f)" % (route, name, taps, errors, error_percent)


        print "============="
        for route, taps in taps_per_route.iteritems():
            print route, taps

    def rank_valid_stops(self):

        stop_list = []
        for stop, value in self._valid_stop_dict.iteritems():
            #print stop, value
            stop_list.append((value, stop))

        stop_list = sorted(stop_list)
        stop_list.reverse()

        for item in stop_list:
            s = self._dataman.get_stop(item[1])
            name = s.get_name()
            print "STOP: %d TAPS: %d NAME: %s" % (item[1], item[0], name)

if __name__ == "__main__":

    runner = Runner()

    runner.run("data/taps_sep_2018.csv")
#     runner.run("data/taps_jan_2018.csv")
    # runner.display_route_data()
    runner.display_date_data()

    runner.rank_valid_stops()
