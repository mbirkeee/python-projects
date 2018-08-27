import simplejson
import os
import time

from constants import KEY
from dataset import SERVICE

LATEST_TIME = (24 * 60 * 60) - 1

def timestr_to_int(input):

    parts = input.split(":")
    result = int(parts[0]) * 60 * 60
    result += int(parts[1]) * 60
    result += int(parts[2])
    return result

def int_to_timestr(input):

    hours = int(input/(60 * 60))
    remain = input - hours * 60 * 60
    minutes = int(remain / 60)
    seconds = remain - minutes * 60
    return "%02d:%02d:%02d" % (hours, minutes, seconds)


class StopTimes(object):

    def __init__(self, base_path, route_mgr):

        self.route_mgr = route_mgr
        self._departure_dict = {}

        self._base_path = base_path
        self._count_duplicate_keys_total = 0

        self._key_counts = {}

        self.read_file()

    def get_data(self):
        return self._departure_dict

    def get_stop_route_departures(self, stop_id, route_id, direction, service_type):
        departures = self.get_stop_departures(stop_id, service_type)
        result = []
        for departure in departures:
            route_id_d = departure.get(KEY.ROUTE_ID)
            direction_d = departure.get(KEY.DIRECTION)
            if route_id_d != route_id:
                continue
            if direction_d != direction:
                continue

            result.append(departure)

        return result

    def get_estimated_wait(self, stop_id, route_id, direction, service_type, time_of_day):
        departures = self.get_stop_route_departures(stop_id, route_id, direction, service_type)
        departure_count = len(departures)
        wait_sec = None

        if departure_count == 0:
            raise ValueError("No departures")

        elif departure_count == 1:
            departure = departures[0]
            depart_time = departure.get(KEY.DEPART_TIME)
            interval = depart_time - time_of_day

            if interval > 0:
                if interval <= (60 * 60):
                    wait_sec = interval

        else:
            after = None
            before = None
            # There is more that 1 departure.
            for departure in departures:
                depart_time = departure.get(KEY.DEPART_TIME)

                # Find the first departure after the time
                if depart_time > time_of_day:
                    if after is None or depart_time < after:
                        after = depart_time

                # Find the most recent departure before the time
                if depart_time < time_of_day:
                    if before is None or depart_time > before:
                        before = depart_time

            print "Time of day: %s" % int_to_timestr(time_of_day)

            if before is not None and after is not None:
                print "Before: %s After: %s" % (int_to_timestr(before), int_to_timestr(after))
                interval = after - before
                if interval > 2 * 60 * 60:
                    print "IGNORE GIANT INTERVAL!!!", interval
                else:
                    wait_sec = interval / 2

            elif after is None:
                # Have missed last departure of the day... return none
                print "Before: %s" % (int_to_timestr(before))

            elif before is None:
                print "After: %s" % (int_to_timestr(after))
                # waiting for first departure of day
                interval = after - time_of_day
                if interval <= (60 * 60):
                    wait_sec = interval

        return wait_sec

    def get_stop_departures(self, stop_id, service_type, start_time=0, stop_time=LATEST_TIME):

        stops = self._departure_dict.get(stop_id)
        if stops is None:
            print "Failed to find departure data for stop: %s (%s)" % (repr(stop_id), self.stops.get_name(stop_id))
            return []

        result = []

        for key, value in stops.iteritems():
            if value.get(KEY.SERVICE_TYPE) == service_type:
                depart_time = value.get(KEY.DEPART_TIME)
                if depart_time >= start_time and depart_time <= stop_time:
                    result.append((depart_time, value))

        result = sorted(result)
        result = [item[1] for item in result]

        return result

    def make_stop_id(self, input):

        try:
            if input.find('_') > 0:
                parts = input.split('_')
                stop_id = int(parts[0])
            else:
                stop_id = int(input)
        except:
            print "Error getting stop ID from: %s" % repr(input)
            stop_id = None

        return stop_id

    def read_file(self):
        """
        From my download

        0 stop_id,
        1 trip_id,
        2 arrival_time,
        3 departure_time,
        4 stop_sequence,
        5 shape_dist_traveled
        """

        file_name = os.path.join(self._base_path, "my-TransitStopTimes.csv")
        line_count = 0
        f = None

        print "StopTimes: Mapping stops to routes..."
        print "StopTimes: Reading file %s..." % file_name

        try:
            start_time = time.time()
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                try:
                    stop_id = self.make_stop_id(parts[0].strip())
                except:
                    print "Failed to get stop id from: %s" % repr(parts[0].strip())
                    stop_id = None

                if stop_id is None:
                    raise ValueError("error!!!")

                # if stop_id == 3432:
                #     raise ValueError("Got stop id 3432")

                if stop_id is None:
                    print "no stop ID"
                    continue

                trip_id = int(parts[1].strip())

                route = self.route_mgr.get_route_from_trip_id(trip_id)

                if route is None:
                    # I think its perfectly valid to fail to get a route ID when there are
                    # two sets of data in the OPEN dataset
                    continue

                    # raise ValueError("Failed to get route for trip ID: %s" % repr(trip_id))

                depart_time_str = parts[3].strip()
                depart_time = timestr_to_int(depart_time_str)

                # print stop_id, trip_id, depart_time
                # print "LINE", line, trip_id, stop_id

                stop = self.route_mgr.get_stop(stop_id)

                if stop is None:
                    raise ValueError("Failed to find stop for stop_id: %d" % stop_id)

                # Cross link the stop / routes
                stop.add_route_id(route.get_id())
                route.add_stop_id(stop_id)

                departure_data = self._departure_dict.get(stop_id, {})

                service_type = self.route_mgr.get_trip_service_type(trip_id)
                headsign = self.route_mgr.get_trip_headsign(trip_id)
                direction = self.route_mgr.get_trip_direction(trip_id)

                key = "%d-%d-%d-%d" % (depart_time, service_type, route.get_id(), direction)

                # print "WANT TO CHECK KEY", key

                if departure_data.has_key(key):
                    self._count_duplicate_keys_total += 1
                    continue

                    # print "Already have departure key", key, depart_time_str, stop_id

                    # raise ValueError("duplicate key")
                    x = self._key_counts.get(key, 0)
                    x += 1
                    self._key_counts[key] = x
                    continue

                if service_type is None:
                    print "failed to get service_id for trip_id", trip_id

                departure_data[key] = {
                        KEY.TRIP_ID         : trip_id,
                        KEY.DEPART_TIME     : depart_time,
                        KEY.SERVICE_TYPE    : service_type,
                        KEY.ROUTE_ID        : route.get_id(),
                        KEY.HEADSIGN        : headsign,
                        KEY.DIRECTION       : direction
                }
                self._departure_dict[stop_id] = departure_data

            read_time = time.time() - start_time
            print "file: %s departures: %d read time: %.2f sec" % (file_name, line_count - 1, read_time)
            print "StopTimes: duplicate departure key count", self._count_duplicate_keys_total

        finally:
            if f:
                f.close()

def test_read():

    f = open("test.json", "r")
    data = simplejson.load(f)
    f.close()
    for k in data.iterkeys():
        print k
    stuff = data.get('d')

    print "Read %s items" % len(stuff)

    # for item in stuff:
    #     print item

if __name__ == "__main__":


    base = '../data/sts/csv/2018_05_04'

    stops = StopTimes(base)

    stop_data = stops.get_data()
    stop_ids = stops.get_stop_ids()

    # sys.exit(0)

    service_dict = {
        SERVICE.MWF: "M-F",
        SERVICE.SAT: "SAT",
        SERVICE.SUN: "SUN"
    }

    for stop_id in stop_ids:
        print "== STOP_ID:", stop_id, "NAME:", stops.get_stop_name(stop_id)

        for service_type, service_desc in service_dict.iteritems():
            departures = stops.get_stop_departures(stop_id, service_type)
            for item in departures:
                trip_id = item.get(KEY.TRIP_ID)
                route_id = item.get(KEY.ROUTE_ID)
                route_name = stops.get_route_name_from_id(route_id)
                route_number = stops.get_route_number_from_id(route_id)
                headsign = item.get(KEY.HEADSIGN)

                t = int_to_timestr(item.get(KEY.DEPART_TIME))
#                print "   %s: Time: %s Route: %s (%s) SIGN: %s (trip_id: %d) route_id: %d" % \
#                      (service_desc, t, route_name, route_number, headsign, trip_id, route_id)

                print "==   %s: Time: %s  %3d : %-30s     SIGN: %s" % \
                      (service_desc, t, int(route_number), route_name, headsign)

             #   display = "   %s: Time: %s Route: %s (%s)" % \
             #         (service_desc, t, route_name, route_number)

              #  length = len(display)

