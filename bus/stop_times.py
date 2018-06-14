import pyproj
import numpy
import math
import time
import simplejson
import os
import sys

import my_utils
from my_utils import UserGPS
from my_utils import TransitData


USE_GOOGLE = True
OPEN_NEW = False

LATEST_TIME = (24 * 60 * 60) - 1

class SERVICE(object):
    UNKNOWN = 0
    MWF     = 1
    SAT     = 2
    SUN     = 3

class KEY(object):
    SERVICE_TYPE    = '1'
    DEPART_TIME     = '2'
    ROUTE_ID        = '3'
    TRIP_ID         = '4'
    HEADSIGN        = '5'

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
        self.read_file()

    def read_file(self):
        """
         0: entityid,
         1: stop_id,
         2: stop_code,
         3: stop_name,
         4: stop_desc,
         5: stop_lat,
         6: stop_lon,
         7: zone_id,
         8: stop_url,
         9: location_type,
        10: parent_station

        From google zip

         0: stop_lat,
         1: wheelchair_boarding,
         2: stop_code,
         3: stop_lon,
         4: stop_timezone,
         5: stop_url,
         6: parent_station,
         7: stop_desc,
         8: stop_name,
         9: location_type,
        10: stop_id,
        11: zone_id
        """
        if USE_GOOGLE:
            file_name = os.path.join(self._base_path, "stops.txt")
        else:
            file_name = os.path.join(self._base_path, "TransitStops.csv")


        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                if USE_GOOGLE:
                    try:
                        stop_id = int(parts[10].strip())
                    except:
                        print "Failed to get stop ID from line", parts

                        try:
                            stop_id = int(parts[2].strip())
                            if not stop_id:
                                raise "bad"
                        except:
                            print "Failed again to get stip ID", parts
                            continue

                        print "USE %d" % stop_id

                    name = parts[8].strip()
                else:
                    try:
                        stop_id = int(parts[1].strip())
                    except:
                        print "Failed to get stop ID from line", parts
                        continue

                    name = parts[3].strip()

                if self._data.get(stop_id):
                    print "Already have stop_id!", stop_id
                    continue

                self._data[stop_id] = name

            print "%s: read %d lines" % (file_name, line_count)

            # for key, value in self._data.iteritems():
            #     print "stop id: %d data: %s" % (key, repr(value))

            return

        finally:
            if f:
                print "closing file"
                f.close()

    def get_name(self, stop_id):
        # print "Getting STOP name for stop id", stop_id
        return self._data.get(stop_id, "Unknown (%d)" % stop_id)

class TransitRoutes(object):

    def __init__(self, base_path):
        self._base_path = base_path
        self._data = {}
        self._duplicates = {}

        self.read_file()

    def read_file(self):
        """

        From downloaded CSV

        0: entityid,
        1: route_id,
        2: agency_id,
        3: route_short_name,
        4: route_long_name,
        5: route_desc,
        6: route_type,
        7: route_url,
        8: route_color,
        9: route_text_color

        From google zip

        0: route_long_name,
        1: route_type,
        2: route_text_color,
        3: route_color,
        4: agency_id,
        5: route_id,
        6: route_url,
        7: route_desc,
        8: route_short_name

        """
        if USE_GOOGLE:
            file_name = os.path.join(self._base_path, "routes.txt")
        else:
            file_name = os.path.join(self._base_path, "TransitRoutes.csv")

        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                if USE_GOOGLE:
                    route_id = int(parts[5].strip())
                    short_name = parts[8].strip()
                    long_name = parts[0].strip()

                    # I am not sure what the route type is
                    route_type = int(parts[1].strip())
                    if route_type != 3:
                        raise ValueError("route type not 3")

                else:
                    route_id = int(parts[1].strip())
                    short_name = parts[3].strip()
                    long_name = parts[4].strip()

                if self._data.get(route_id):
                    raise ValueError("already have", route_id)
                    continue


                if route_id <= 10080:
                    self._data[route_id] = (short_name, long_name)
                else:
                    self._duplicates[route_id] = (short_name, long_name)

                #duplicate_route_id = self.find_duplicate_route(short_name, long_name)

#            for key, value in self._data.iteritems():
#                print "route id: %d data: %s" % (key, repr(value))

            temp = {}
            for route_id, value in self._duplicates.iteritems():
                short_name = value[0]
                long_name = value[1]
                duplicate_route_id = self.find_duplicate_route(short_name, long_name)
                if duplicate_route_id is None:
                    raise ValueError("no duplicate for %d" % key)
                temp[route_id] = duplicate_route_id

            self._duplicates = temp
#            for route_id, value in self._duplicates.iteritems():
#                print "duplicate for route id: %d --> %s" % (route_id, repr(value))

            print len(self._data)
            print len(self._duplicates)

            print "%s: read %d lines" % (file_name, line_count)

        finally:
            if f:
                print "closing file"
                f.close()


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

        OPEN_NEW

         0: entityid,
         1: block_id,
         2: bikes_allowed,
         3: route_id,
         4: wheelchair_accessible,
         5: direction_id,
         6: trip_headsign,
         7: shape_id,
         8: service_id,
         9: trip_id,
        10: trip_short_name

        From downloaded CSV
        0: entityid,
        1: route_id,
        2: service_id,
        3: trip_id,
        4: trip_headsign,
        5: direction_id,
        6: block_id,
        7: shape_id

        Froom google zip file
        0: block_id,
        1: bikes_allowed,
        2: route_id,
        3: wheelchair_accessible,
        4: direction_id,
        5: trip_headsign,
        6: shape_id,
        7: service_id,
        8: trip_id,
        9: trip_short_name
        """

        if USE_GOOGLE:
            file_name = os.path.join(self._base_path, "trips.txt")
        else:
            file_name = os.path.join(self._base_path, "TransitTrips.csv")

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

                if USE_GOOGLE:
                    route_id = int(parts[2].strip())
                    service_type = self.make_service_type_from_google_data(parts[7].strip())
                    trip_id = int(parts[8].strip())
                    headsign = parts[5].strip()
                elif OPEN_NEW:
                    route_id = int(parts[3])
                    service_type = self.make_service_type_from_google_data(parts[8].strip())
                    trip_id = int(parts[9].strip())
                    headsign = parts[6].strip()
                else:
                    route_id = int(parts[1].strip())
                    service_type = int(parts[2].strip())
                    trip_id = int(parts[3].strip())
                    headsign = parts[6].strip()

                if self._data.get(trip_id):
                    print "ALREADY HAVE TRIP ID!!!!!!", trip_id
                    continue

                self._data[trip_id] = (route_id, service_type, headsign)

            print "read %d lines" % line_count
            read_time = time.time() - start_time
            print "%s: read time: %.2f" % (file_name, read_time)

            #for key, value in self._data.iteritems():
            #    print "Trip ID", key, "Data:", value

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

        self.trips = TransitTrips(base_path)
        self.routes = TransitRoutes(base_path)
        self.stops = Stops(base_path)

        self._data = {}

        self._route_id_dict = {}

        self._base_path = base_path

        self._count_duplicate = 0
        self._count_primary = 0

        self._count_duplicate_keys_total = 0

        self._key_counts = {}

        self.read_file()


    def get_stop_name_from_id(self, stop_id):
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
        From google zipfile

        0: trip_id,
        1: arrival_time,
        2: departure_time,
        3: stop_id,
        4: stop_sequence,
        5: stop_headsign,
        6: pickup_type,
        7: drop_off_type,
        8: shape_dist_traveled,
        9: timepoint

        From CSV download

        0: entityid,
        1: trip_id,
        2: arrival_time,
        3: departure_time,
        4: stop_id,
        5: stop_sequence,
        6: stop_headsign,
        7: pickup_type,
        8: drop_off_type,
        9: shape_dist_traveled

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

        if USE_GOOGLE:
            file_name = os.path.join(self._base_path, "stop_times.txt")
        else:
            file_name = os.path.join(self._base_path, "TransitStopTimes.csv")

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

                if USE_GOOGLE:
                    trip_id = int(parts[0].strip())
                    depart_time_str = parts[2].strip()

                    try:
                        stop_id = self.make_stop_id_from_google(parts[3].strip())
                    except:
                        print "Failed to get stop id from: %s" % repr(parts[3].strip())
                        stop_id = None
                else:
                    trip_id = int(parts[1].strip())
                    depart_time_str = parts[3].strip()
                    stop_id = int(parts[4].strip())

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

                # print depart_time, service_type, route_id

                if USE_GOOGLE:
                    # key = "%d-%d-%s-%s" % (depart_time, service_type, route_name, headsign)
                    key = "%d-%d-%d" % (depart_time, service_type, route_id)
                else:
                    key = "%d-%d-%d" % (depart_time, service_type, route_id)

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
                        KEY.HEADSIGN : headsign
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


def test_fetch():

    import urllib
    import urllib2

    base = "http://opendata-saskatoon.cloudapp.net:8080/v1/SaskatoonOpenDataCatalogueBeta"


    # This seems to work to get data for just one stop
#    url = "TransitStopTimes?$filter=%s&format=json" % urllib.quote("stop_id eq '3094'")

    # Get stops from 3000 to 4000
    url = "TransitStops?$filter=%s&format=json" % urllib.quote("stop_id ge '3000' and stop_id lt '4000'")


    url = "%s/%s" % (base, url)
    print url
    # raise ValueError("DONE")
    #url = 'http://opendata-saskatoon.cloudapp.net/DataBrowser/DownloadCsv?container=SaskatoonOpenDataCatalogueBeta&entitySet=TransitStops'

    response = urllib2.urlopen(url)
    print "Response:", response
    json = response.read()
    response.close()
    f = open("test.json", "w")
    f.write(json)
    f.close()

def test_read():

    f = open("test.json", "r")
    data = simplejson.load(f)
    f.close()
    for k in data.iterkeys():
        print k
    stuff = data.get('d')
    for item in stuff:
        print item
    print len(stuff)

if __name__ == "__main__":


    test_fetch()
    test_read()
    sys.exit(0)

    if USE_GOOGLE:
        base = '../data/sts/csv/2018_05_04'
    else:
        base = '../../bus-data/open_data/2018_05_04'


    stops = StopTimes(base)

    stop_data = stops.get_data()
    stop_ids = stops.get_stop_ids()

#    sys.exit(0)

    service_dict = {
        SERVICE.MWF: "MWF",
        SERVICE.SAT: "SAT",
        SERVICE.SUN: "SUN"
    }

    for stop_id in stop_ids:
        print "== STOP_ID:", stop_id, "NAME:", stops.get_stop_name_from_id(stop_id)

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

