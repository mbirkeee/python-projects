import pyproj
import numpy
import math
import time
import simplejson
import os
import scandir
import pickle

import my_utils
from my_utils import UserGPS
from my_utils import TransitData

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

class TransitRoutes(object):

    def __init__(self, base_path):
        self._base_path = base_path
        self._data = {}
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

        # file_name = os.path.join(self._base_path, "TransitRoutes.csv")

        file_name = os.path.join(self._base_path, "routes.txt")
        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                route_id = int(parts[5].strip())
                short_name = parts[8].strip()
                long_name = parts[0].strip()

                if self._data.get(route_id):
                    print "ALREADY HAVE ROUTE ID!!!!!!", route_id
                    continue

                self._data[route_id] = (short_name, long_name)

            print "%s: read %d lines" % (file_name, line_count)

            for key, value in self._data.iteritems():
                print "route id: %d data: %s" % (key, repr(value))
            return

        finally:
            if f:
                print "closing file"
                f.close()

    def get_route_name_from_id(self, route_id):
        data = self._data.get(route_id)
        if data is None:
            return "Unknown"
        return data[1]

    def get_route_number_from_id(self, route_id):
        data = self._data.get(route_id)
        if data is None:
            return "Unknown"
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

        # file_name = os.path.join(self._base_path, "TransitTrips.csv")
        file_name = os.path.join(self._base_path, "trips.txt")
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

                route_id = int(parts[2].strip())
                # service_id = int(parts[7].strip())
                service_type = self.make_service_type_from_google_data(parts[7].strip())
                trip_id = int(parts[8].strip())

                if self._data.get(trip_id):
                    print "ALREADY HAVE TRIP ID!!!!!!", trip_id
                    continue

                self._data[trip_id] = (route_id, service_type)

            print "read %d lines" % line_count
            read_time = time.time() - start_time
            print "%s: read time: %.2f" % (file_name, read_time)

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

class StopTimes(object):

    def __init__(self, base_path):

        self.trips = TransitTrips(base_path)
        self.routes = TransitRoutes(base_path)

        self._data = {}

        self._route_id_dict = {}

        self._base_path = base_path
        self.read_file()


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

    def get_stop_departures(self, stop_id, service_type):

        stops = self._data.get(stop_id)
        if stops is None:
            print "Failed to find departure data for stop: %s" % repr(stop_id)
            return []

        result = []

        for key, value in stops.iteritems():
            if value.get(KEY.SERVICE_TYPE) == service_type:
                result.append(value)

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

        return stop_id

    def read_file(self):
        """
        # From CSV download
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

        # From google zipfile
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

        # file_name = os.path.join(self._base_path, "TransitStopTimes.csv")
        file_name = os.path.join(self._base_path, "stop_times.txt")
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

                trip_id = int(parts[0].strip())
                depart_time = parts[2].strip()

                try:
                    stop_id = self.make_stop_id_from_google(parts[3].strip())
                except:
                    print "Failed to get stop id from: %s" % repr(parts[3].strip())
                    stop_id = None

                if stop_id is None: continue

                # print stop_id, trip_ip, depart_time
                # print "LINE", line.strip()

                stop_data = self._data.get(stop_id, {})

                key = "%d-%s" % (trip_id, depart_time)

                if stop_data.has_key(key):
                    print "Already have key", key
                    continue

                route_id = self.trips.get_route_id(trip_id)
                service_type = self.trips.get_service_type(trip_id)

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
                        KEY.ROUTE_ID : route_id
                }
                self._data[stop_id] = stop_data

            print "read %d lines" % line_count
            read_time = time.time() - start_time
            print "file: %s read time: %.2f sec" % (file_name, read_time)

            # for route_id, count in self._route_id_dict.iteritems():
            #     print "route_id", route_id, count


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

if __name__ == "__main__":

    base = 'data/open_data/google_zip/2018_05_04'

    stops = StopTimes(base)
    # trips = TransitTrips(base)
    # routes = TransitRoutes(base)

    stop_data = stops.get_data()
    stop_ids = stops.get_stop_ids()

    for stop_id in stop_ids:
        print "STOP ID:", stop_id
        departures = stops.get_stop_departures(stop_id, SERVICE.MWF)
        for item in departures:
            # print repr(item)
            route_id = item.get(KEY.ROUTE_ID)
            route_name = stops.get_route_name_from_id(route_id)
            route_number = stops.get_route_number_from_id(route_id)
            print "   MWF: Time: %s Route: %s (%s)" % (repr(item.get(KEY.DEPART_TIME)), route_name, route_number)

        departures = stops.get_stop_departures(stop_id, SERVICE.SAT)
        for item in departures:
            # print repr(item)
            route_id = item.get(KEY.ROUTE_ID)
            route_name = stops.get_route_name_from_id(route_id)
            route_number = stops.get_route_number_from_id(route_id)
            print "   SAT: Time: %s Route: %s (%s)" % (repr(item.get(KEY.DEPART_TIME)), route_name, route_number)


        departures = stops.get_stop_departures(stop_id, SERVICE.SUN)
        for item in departures:
            # print repr(item)
            route_id = item.get(KEY.ROUTE_ID)
            route_name = stops.get_route_name_from_id(route_id)
            route_number = stops.get_route_number_from_id(route_id)
            print "   SUN: Time: %s Route: %s (%s)" % (repr(item.get(KEY.DEPART_TIME)), route_name, route_number)

    # for stop_id, stop_data in stop_data.iteritems():
    #     print "STOP ID: %d" % stop_id
    #
    #
    #     for key, trip_data in stop_data.iteritems():
    #         trip_id = trip_data[0]
    #         route_id = trips.get_route_id(trip_id)
    #
    #         print "    TRIP ID: %d DEPART TIME: %s ROUTE: %s" % (trip_id, trip_data[1], repr(route_id))
