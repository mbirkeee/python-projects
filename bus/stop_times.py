import pyproj
import numpy
import math
import time
import simplejson
import os
import scandir

import my_utils
from my_utils import UserGPS
from my_utils import TransitData

class TransitRoutes(object):

    def __init__(self, base_path):
        self._base_path = base_path
        self._data = {}
        self.read_file()

    def read_file(self):
        """
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
        """

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

                route_id = int(parts[1].strip())
                short_name = parts[3].strip()
                long_name = parts[4].strip()

                if self._data.get(route_id):
                    print "ALREADY HAVE ROUTE ID!!!!!!", route_id
                    continue

                self._data[route_id] = (short_name, long_name)

            print "read %d lines" % line_count
            # print self._trip_data

            # j = open(file_name_json, 'w')
            # simplejson.dump(self._trip_data, j, indent=4)
            # j.close()

            for key, value in self._data.iteritems():
                print "route id: %d data: %s" % (key, repr(value))
            return

        finally:
            if f:
                print "closing file"
                f.close()

class TransitTrips(object):

    def __init__(self, base_path):
        self._base_path = base_path
        self._trip_data = {}
        self.read_file()

    def read_file(self):
        """
        0: entityid,
        1: route_id,
        2: service_id,
        3: trip_id,
        4: trip_headsign,
        5: direction_id,
        6: block_id,
        7: shape_id
        """
        file_name_json = os.path.join(self._base_path, "TransitTrips.json")

        try:
            f = open(file_name_json, 'r')
            self._trip_data = simplejson.load(f)
            f.close()
            found = True
        except Exception as err:
            print "Exception: %s: %s" % (repr(err), file_name_json)
            found = False

        if found:
            print "read TransitTrip data from JSON"
            return

        file_name = os.path.join(self._base_path, "TransitTrips.csv")
        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                route_id = int(parts[1].strip())
                service_id = int(parts[2].strip())
                trip_id = int(parts[3].strip())

                if self._trip_data.get(trip_id):
                    print "ALREADY HAVE TRIP ID!!!!!!", trip_id
                    continue

                self._trip_data[trip_id] = (route_id, service_id)

            print "read %d lines" % line_count
            # print self._trip_data

            # j = open(file_name_json, 'w')
            # simplejson.dump(self._trip_data, j, indent=4)
            # j.close()

            return

        finally:
            if f:
                print "closing file"
                f.close()

    def get_route_id(self, trip_id):
        # print "get route id for trip: %d" % trip_id
        data = self._trip_data.get(trip_id)
        if data is None:
            return None
        return data[0]

    def get_service_id(self, trip_id):
        data = self._trip_data.get(trip_id)
        if data is None:
            return None
        return data[1]

class StopTimes(object):


    def __init__(self, base_path):

        self._stop_time_data = {}
        self._base_path = base_path
        self.read_file()

        # self._trips = TransitTrips(self._base_path)

        # self.print_data()

    def print_data(self):

        for stop_id, stop_data in self._stop_time_data.iteritems():
            print "STOP ID: %d" % stop_id

            for key, trip_data in stop_data.iteritems():
                trip_id = trip_data[0]
                route_id = self._trips.get_route_id(trip_id)

                print "    TRIP ID: %d DEPART TIME: %s ROUTE: %s" % (trip_id, trip_data[1], repr(route_id))

    def read_file(self):
        """
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

        file_name_json = os.path.join(self._base_path, "TransitStopTimes.json")

        try:
            f = open(file_name_json, 'r')
            self._stop_time_data = simplejson.load(f)
            f.close()
            found = True
        except Exception as err:
            print "Exception: %s: %s" % (repr(err), file_name_json)
            found = False

        if found:
            print "read TransitStopTimes data from JSON"
            return

        file_name = os.path.join(self._base_path, "TransitStopTimes.csv")
        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                trip_id = int(parts[1].strip())
                depart_time = parts[3].strip()
                stop_id = int(parts[4].strip())

                # print stop_id, trip_ip, depart_time
                # print "LINE", line.strip()

                stop_data = self._stop_time_data.get(stop_id, {})

                key = "%d-%s" % (trip_id, depart_time)

                if stop_data.has_key(key):
                    print "Already have key", key
                    # raise ValueError("stop!!")
                else:
                    stop_data[key] = (trip_id, depart_time)

                self._stop_time_data[stop_id] = stop_data

            print "read %d lines" % line_count

            # j = open(file_name_json, 'w')
            # simplejson.dump(self._stop_time_data, j, indent=4)
            # j.close()

        finally:
            if f:
                print "closing file"
                f.close()

if __name__ == "__main__":

    base = 'data/open_data/2018_05_04'

    #stops = StopTimes(base)
    #trips = TransitTrips(base)
    routes = TransitRoutes(base)

