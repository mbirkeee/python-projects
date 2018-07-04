import pyproj
import numpy
import math
import time
import simplejson
import os
import sys
import time

# import my_utils
# from my_utils import UserGPS
# from my_utils import TransitData

LATEST_TIME = (24 * 60 * 60) - 1

class SERVICE(object):
    UNKNOWN = 0
    MWF     = 1
    SAT     = 2
    SUN     = 3

class KEY(object):
    SERVICE_TYPE    = 'serv_type'
    DEPART_TIME     = 'depart_time'
    ROUTE_ID        = 'route_id'
    TRIP_ID         = 'trip_id'
    HEADSIGN        = 'headsign'
    DIRECTION       = 'direction'
    STOP_ID         = 'stop_id'
    EST_WAIT_SEC    = 'est_wait_sec'
    DISTANCE        = 'dist'
    POPULATION      = 'pop'
    WEIGHT          = 'weight'

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


class Stops(object):

    def __init__(self, base_path):

        self._base_path = base_path
        self._data = {}
        self._myproj = pyproj.Proj("+init=EPSG:32613")
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

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                try:
                    parts = line.split(",")
                    stop_code = int(parts[1].strip())
                    name = parts[6].strip()
                    lat = float(parts[2].strip())
                    lon = float(parts[3].strip())

                    print stop_code, lat, lon, name

                    x, y  = self._myproj(lon, lat)
                    stop_data = {
                        'lat'   : lat,
                        'lon'   : lon,
                        'x'     : x,
                        'y'     : y,
                        'name'  : name
                    }

                    result[stop_code] = stop_data

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

    def get_utm(self, stop_id):
        stop_data = self._data.get(stop_id)
        if stop_data is None:
            return None
        return (stop_data.get('x'), stop_data.get('y'))

    def get_lat_lon(self, stop_id):
        stop_data = self._data.get(stop_id)
        if stop_data is None:
            return None
        return (stop_data.get('lat'), stop_data.get('lon'))


class TransitShapes(object):

    def __init__(self, base_path):

        self._june_data = False
        if base_path.find("2018_05_04") > 0:
            print "this is the JUNE data"
            self._june_data = True
        else:
            print "this is the JULY data"

        self._base_path = base_path
        self._data = {}
        self.read_file()
        self.sort_data()

    def sort_data(self):

        result = {}

        for shape_id, points in self._data.iteritems():
            result[shape_id] = sorted(points)

        for shape_id, points in result.iteritems():
            # print "shape_id", shape_id
            for item in points:
                print item

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

        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")
                print parts

                shape_id = int(parts[0].strip())
                lat = float(parts[1].strip())
                lon = float(parts[2].strip())
                seq = int(parts[3].strip())

                points = self._data.get(shape_id, [])
                points.append((seq, lat, lon))
                self._data[shape_id] = points

            # raise ValueError("temp stop")

        finally:
            if f:
                f.close()

class TransitRoutes(object):

    def __init__(self, base_path):

        self._june_data = False
        if base_path.find("2018_05_04") > 0:
            print "this is the JUNE data"
            self._june_data = True
        else:
            print "this is the JULY data"

        self._base_path = base_path
        self._data = {}
        self._duplicates = {}
        self.read_file()

    def read_file(self):
        """
        0 route_id,
        1 route_type,
        2 route_color,
        3 text_color,
        4 name_short,
        5 name_long

        """
        file_name = os.path.join(self._base_path, "my-TransitRoutes.csv")

        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                route_id = int(parts[0].strip())
                short_name = parts[4].strip()
                long_name = parts[5].strip()

                # I am not sure what the route type is
                route_type = int(parts[1].strip())

                if route_type != 3:
                    raise ValueError("route type not 3")

                print "read route ID", route_id


                if self._june_data:
                    if route_id > 10080:
                        self._duplicates[route_id] = (short_name, long_name)
                        continue

                if self._data.has_key(route_id):
                    raise ValueError("THIS IS A DUP!!!")

                self._data[route_id] = (short_name, long_name)

                #duplicate_route_id = self.find_duplicate_route(short_name, long_name)

#            for key, value in self._data.iteritems():
#                print "route id: %d data: %s" % (key, repr(value))

            temp = {}
            for route_id, value in self._duplicates.iteritems():
                short_name = value[0]
                long_name = value[1]
                duplicate_route_id = self.find_duplicate_route(short_name, long_name)
                if duplicate_route_id is None:
                    raise ValueError("no duplicate for %d" % route_id)
                    # continue

                temp[route_id] = duplicate_route_id

            self._duplicates = temp
#            for route_id, value in self._duplicates.iteritems():
#                print "duplicate for route id: %d --> %s" % (route_id, repr(value))

            print "number of routes:", len(self._data)
            print "number of duplicates:", len(self._duplicates)

            print "%s: read %d lines" % (file_name, line_count)

        finally:
            if f:
                print "closing file"
                f.close()

        #raise ValueError("temp stop")

    def get_primary_route_id(self, route_id):
        primary_id = self._duplicates.get(route_id)
        return primary_id

    def find_duplicate_route(self, short_name, long_name):

        duplicate_route_id = None
        for route_id, data in self._data.iteritems():
            # print "compare %s %s to %s" % (short_name, long_name, data)
            if short_name == data[0] and long_name == data[1]:
                duplicate_route_id = route_id
                break

        # if duplicate_route_id is not None:
        #     print "Found the match!!!"

        return duplicate_route_id

    def get_route_name_from_id(self, route_id):
        data = self._data.get(route_id)
        if data is None:
            return "Unknown: %s" % repr(route_id)
        return data[1]

    def get_route_number_from_id(self, route_id):
        data = self._data.get(route_id)
        if data is None:
            return "Unknown: %s" % repr(route_id)
        return data[0]

class TransitTrips(object):

    def __init__(self, base_path):
        self._base_path = base_path
        self._data = {}
        self._route_id_to_shape_id = {}

        self.read_file()

    def make_service_type_from_google_data(self, input):

        try:
            service_type = int(input[0])

            if service_type not in [SERVICE.MWF, SERVICE.SAT, SERVICE.SUN]:
                raise ValueError("Invalid service type")

        except Exception as err:
            print "%s: Error getting service type from: %s" % (repr(err), repr(input))
            service_type = SERVICE.UNKNOWN

        return service_type


    def read_file(self):

        """
        0 trip_id,
        1 route_id,
        2 block_id,
        3 shape_id,
        4 service_id,
        5 direction,
        6 bikes,
        7 wheelchairs,
        8 headsign
        """

        file_name = os.path.join(self._base_path, "my-TransitTrips.csv")

        line_count = 0
        f = None

        try:
            start_time = time.time()
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                route_id = int(parts[1].strip())
                service_type = self.make_service_type_from_google_data(parts[4].strip())
                trip_id = int(parts[0].strip())
                shape_id = int(parts[3].strip())

                headsign = parts[8].strip()
                direction = int(parts[5].strip())

                if self._data.get(trip_id):
                    print "ALREADY HAVE TRIP ID!!!!!!", trip_id
                    continue

                self._data[trip_id] = (route_id, service_type, headsign, direction, shape_id)

                # This section maps route_id to shape_id
                shape_id_list = self._route_id_to_shape_id.get(route_id, [])
                shape_id_list.append(shape_id)
                shape_id_list = list(set(shape_id_list))
                self._route_id_to_shape_id[route_id] = shape_id_list

                # if not self._route_id_to_shape_id.has_key(route_id):
                #     print "Added route_id -> shape_id", route_id, shape_id
                #     self._route_id_to_shape_id[route_id] = shape_id
                # else:
                #     have_shape_id = self._route_id_to_shape_id.get(route_id)
                #     if have_shape_id != shape_id:
                #         msg = "WARNING: shape id mismatch: route_id: %s have: %s got: %s!!!!" % \
                #                          (route_id, have_shape_id, shape_id)
                #         print msg

            print "read %d lines" % line_count
            read_time = time.time() - start_time
            print "%s: read time: %.2f" % (file_name, read_time)

            for key, value in self._route_id_to_shape_id.iteritems():
                print "Route ID: %s shape_ids: %s" % (repr(key), repr(value))

            #for key, value in self._data.iteritems():
            #    print "Trip ID", key, "Data:", value

            # raise ValueError('temp stop')

            return

        finally:
            if f:
                print "closing file"
                f.close()

    def get_route_id(self, trip_id):
        # print "get route id for trip: %d" % trip_id
        data = self._data.get(trip_id)
        if data is None:
            return None
        return data[0]

    def get_direction(self, trip_id):
        data = self._data.get(trip_id)
        if data is None:
            return None
        return data[3]

    def get_service_type(self, trip_id):
        data = self._data.get(trip_id)
        if data is None:
            return None
        return data[1]

    def get_headsign(self, trip_id):
        data = self._data.get(trip_id)
        if data is None:
            return None
        return data[2]

class StopTimes(object):

    def __init__(self, base_path):


        if base_path.find("2018_05_04") > 0:
            print "this is the JUNE data"
        else:
            print "this is the JULY data"

        self.trips = TransitTrips(base_path)
        self.routes = TransitRoutes(base_path)
        self.shapes = TransitShapes(base_path)

        self.stops = Stops(base_path)

        self._data = {}

        self._route_id_dict = {}

        self._base_path = base_path

        self._count_duplicate = 0
        self._count_primary = 0

        self._count_duplicate_keys_total = 0

        self._key_counts = {}

        self.read_file()


    def get_stop_lat_lon(self, stop_id):
        return self.stops.get_lat_lon(stop_id)

    def get_stop_utm(self, stop_id):
        return self.stops.get_utm(stop_id)

    def get_stop_name(self, stop_id):
        return self.stops.get_name(stop_id)

    def get_route_name_from_id(self, route_id):
        # return "name_%d" % route_id
        return self.routes.get_route_name_from_id(route_id)

    def get_route_number_from_id(self, route_id):
        # return "number_%d" % route_id
        return self.routes.get_route_number_from_id(route_id)

    def get_data(self):
        return self._data

    def get_stop_ids(self):

        stop_ids = [key for key in self._data.iterkeys()]
        return stop_ids


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

        return 1000



    def get_stop_departures(self, stop_id, service_type, start_time=0, stop_time=LATEST_TIME):

        stops = self._data.get(stop_id)
        if stops is None:
            print "Failed to find departure data for stop: %s" % repr(stop_id)
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

    def make_stop_id_from_google(self, input):

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

        # NOTE: It appears to be faster to read and process the CSV file than to load the data from a pickle
        # file_name_pickle = os.path.join(self._base_path, "TransitStopTimes.pickle")
        # try:
        #     start_time = time.time()
        #     self._data = pickle.load( open( file_name_pickle, "rb" ))
        #     read_time = time.time() - start_time
        #     print "pickle read time: %.2f sec" % read_time
        # except:
        #     self._data = None
        #
        # if self._data is not None:
        #     print "loaded data from pickle"
        #     return

        file_name = os.path.join(self._base_path, "my-TransitStopTimes.csv")
        line_count = 0
        f = None

        try:
            start_time = time.time()
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                trip_id = int(parts[1].strip())
                depart_time_str = parts[3].strip()

                try:
                    stop_id = self.make_stop_id_from_google(parts[0].strip())
                except:
                    print "Failed to get stop id from: %s" % repr(parts[0].strip())
                    stop_id = None

                depart_time = timestr_to_int(depart_time_str)
                #print "%s -> %d -> %s" % (depart_time_str, depart_time, int_to_timestr(depart_time))

                if stop_id is None:
                    print "no stop ID"
                    continue

                # print stop_id, trip_ip, depart_time
                # print "LINE", line, trip_id, stop_id

                stop_data = self._data.get(stop_id, {})

                route_id = self.trips.get_route_id(trip_id)
                service_type = self.trips.get_service_type(trip_id)
                headsign = self.trips.get_headsign(trip_id)
                direction = self.trips.get_direction(trip_id)
                route_name = self.get_route_name_from_id(route_id)

                primary_route_id = self.routes.get_primary_route_id(route_id)
                if primary_route_id is None:
                    # This is a primary route
                    self._count_primary += 1
                else:
                    # This is a duplicate route
                    self._count_duplicate +=1

                if primary_route_id is not None:
                    # Do not include duplicate routes in result
                    continue

                # print depart_time, service_type, route_id, direction
                key = "%d-%d-%d-%d" % (depart_time, service_type, route_id, direction)

                if stop_data.has_key(key):
                    # print "Already have key", key, depart_time_str, stop_id
                    x = self._key_counts.get(key, 0)
                    x += 1
                    self._key_counts[key] = x
                    self._count_duplicate_keys_total += 1
                    continue

                if route_id is None:
                    print "failed to get route_id ID", trip_id

                else:
                    count = self._route_id_dict.get(route_id, 0)
                    count += 1
                    self._route_id_dict[route_id] = count

                if service_type is None:
                    print "failed to get service_id for trip_id", trip_id

                stop_data[key] = {
                        KEY.TRIP_ID: trip_id,
                        KEY.DEPART_TIME : depart_time,
                        KEY.SERVICE_TYPE : service_type,
                        KEY.ROUTE_ID : route_id,
                        KEY.HEADSIGN : headsign,
                        KEY.DIRECTION : direction
                }
                self._data[stop_id] = stop_data

            print "read %d lines" % line_count
            read_time = time.time() - start_time
            print "file: %s read time: %.2f sec" % (file_name, read_time)

            print "primary count", self._count_primary
            print "duplicate count", self._count_duplicate
            print "duplicate_key count", self._count_duplicate_keys_total

            # for route_id, count in self._route_id_dict.iteritems():
            #     print "route_id", route_id, count

            #for k, v in self._key_counts.iteritems():
            #    print k, v

            # start_time = time.time()
            # pickle.dump( self._data, open( file_name_pickle, "wb" ) )
            # write_time = time.time() - start_time
            # print "pickle write time: %.2f sec" % write_time

            # j = open(file_name_json, 'w')
            # simplejson.dump(self._stop_time_data, j, indent=4)
            # j.close()

        finally:
            if f:
                print "closing file"
                f.close()


# def test_fetch():
#
#     import urllib
#     import urllib2
#
#     base = "http://opendata-saskatoon.cloudapp.net:8080/v1/SaskatoonOpenDataCatalogueBeta"
#
#
#     # This seems to work to get data for just one stop
# #    url = "TransitStopTimes?$filter=%s&format=json" % urllib.quote("stop_id eq '3094'")
#
#     table = "TransitStopTimes"
#
#     # Get stops from 3000 to 4000
# #    url = "TransitStops?$filter=%s&format=json" % urllib.quote("stop_id ge '3000' and stop_id lt '4000'")
#
#
#     next_partition_key = None
#     next_row_key = None
#     index = 0
#
#     while True:
#
#         if next_partition_key is None:
#             url = "%s/%s?format=json" % (base, table)
#         else:
#             url = "%s/%s?NextPartitionKey=%s&NextRowKey=%s&format=json" % \
#                   (base, table, next_partition_key, next_row_key)
#
#         print url
#     # raise ValueError("DONE")
#     #url = 'http://opendata-saskatoon.cloudapp.net/DataBrowser/DownloadCsv?container=SaskatoonOpenDataCatalogueBeta&entitySet=TransitStops'
#
#
#         response = urllib2.urlopen(url)
#     # print "Response:", response, repr(response)
#
#         json = response.read()
#
#         response.close()
#
#         d = simplejson.loads(json)
#         stuff = d.get('d')
#         print "READ %d items" % len(stuff)
#
#         info = response.info()
#         next_partition_key = info.get('x-ms-continuation-NextPartitionKey')
#         next_row_key = info.get('x-ms-continuation-NextRowKey')
#
#         print "next_partition", next_partition_key
#         print "next_row", next_row_key
#
#         f = open("transit_stops_%d.json" % index, "w")
#         f.write(json)
#         f.close()
#
#         index += 1
#         if next_partition_key is None:
#             break
#
#         time.sleep(1)
#
#     print "Done"
#     #next_row_key = info.getHeader('x-ms-continuation-NextRowKey')



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

