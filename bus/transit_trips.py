import os
import time

from route_id_names import ROUTE_IDS_05_04
from route_id_names import ROUTE_IDS_06_21
from route_id_names import BAD_SHAPES

from constants import SERVICE

class TransitTrips(object):

    def __init__(self, base_path):

        if base_path.find("2018_05_04") > 0:
            print "TransitTrips: using JUNE data"
            self._include_route_dict = ROUTE_IDS_05_04
        else:
            print "TransitTrips: using JULY/AUG data"
            self._include_route_dict = ROUTE_IDS_06_21

        self._base_path = base_path
        self._trip_dict = {}
        self._route_id_to_shape_id = {}
        self.read_file_trips()

    def make_service_type(self, input):

        try:
            service_type = int(input[0])

            if service_type not in [SERVICE.MWF, SERVICE.SAT, SERVICE.SUN]:
                raise ValueError("Invalid service type")

        except Exception as err:
            print "%s: Error getting service type from: %s" % (repr(err), repr(input))
            service_type = SERVICE.UNKNOWN

        return service_type


    def read_file_trips(self):

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

        print "Reading transit trips file: %s" % file_name

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

                if not self._include_route_dict.has_key(route_id):
                    # print "SKIPPING TRIP"
                    continue

                service_type = self.make_service_type(parts[4].strip())
                trip_id = int(parts[0].strip())
                shape_id = int(parts[3].strip())

                headsign = parts[8].strip()
                direction = int(parts[5].strip())

                if self._trip_dict.get(trip_id):
                    print "ALREADY HAVE TRIP ID!!!!!!", trip_id
                    continue

                self._trip_dict[trip_id] = (route_id, service_type, headsign, direction, shape_id)

                # This section maps route_id to shape_id

                # print "WANT TO MAP SHAPE_ID", shape_id, "TO ROUTE ID", route_id
                bad_shapes = BAD_SHAPES.get(route_id, [])
                if shape_id in bad_shapes:
                    print "punt bad shape_id %s for route_id %s (trip_id: %s)" % \
                          (repr(shape_id), repr(route_id), repr(trip_id))
                    continue

                shape_id_list = self._route_id_to_shape_id.get(route_id, [])
                shape_id_list.append(shape_id)
                shape_id_list = list(set(shape_id_list))
                self._route_id_to_shape_id[route_id] = shape_id_list

            print "read %d lines" % line_count
            read_time = time.time() - start_time
            print "%s: read time: %.2f" % (file_name, read_time)

            # For testing/debugging
            # for key, value in self._route_id_to_shape_id.iteritems():
            #     print "Route ID: %s shape_ids: %s" % (repr(key), repr(value))

            #for key, value in self._data.iteritems():
            #    print "Trip ID", key, "Data:", value
            # raise ValueError('temp stop')

            print "Read %d items from: %s" % (len(self._trip_dict), file_name)

            return

        finally:
            if f:
                f.close()


    def get_route_id(self, trip_id):
        # print "get route id for trip: %d" % trip_id
        data = self._trip_dict.get(trip_id)
        if data is None:
            return None
        return data[0]

    def get_direction(self, trip_id):
        data = self._trip_dict.get(trip_id)
        if data is None:
            return None
        return data[3]

    def get_service_type(self, trip_id):
        data = self._trip_dict.get(trip_id)
        if data is None:
            return None
        return data[1]

    def get_headsign(self, trip_id):
        data = self._trip_dict.get(trip_id)
        if data is None:
            return None
        return data[2]

    def get_shape_ids(self, route_id):
        return self._route_id_to_shape_id.get(route_id)

