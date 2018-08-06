import os
import math

from my_utils import DaData
from my_utils import get_point_dist
from stops import TransitStops
from stop_times import StopTimes
from stop_times import SERVICE
from stop_times import KEY
from route_id_names import ROUTE_IDS_05_04
from route_id_names import ROUTE_IDS_06_21

class Intersect(object):

    def __init__(self):
        self._data = {}
        self.da_centroids = DaData()

    def load(self, file_name, expected_parts=None, stop_index=None, da_index=None):

        count = 0
        f = open(file_name, 'r')
        for line in f:
            count += 1
            if count == 1: continue

            line = line.strip()
            parts = line.split(',')
            # print len(parts)
            if len(parts) != expected_parts:
                raise ValueError("Unexpected number of parts")

            # print "LINE", line

            stop_id = int(parts[stop_index].strip())
            da_id = int(parts[da_index].strip())

            # print "stop_id", stop_id, "da_id", da_id

            # This just checks that the DA is known
            pop = self.da_centroids.get_population(da_id)
            if pop is None:
                raise ValueError("dont know about DA: %s" % repr(da_id))

            da_list = self._data.get(stop_id, [])
            if da_id in da_list:
                raise ValueError("already know about da_id: %s stop_id:%s" % (repr(da_id), repr(stop_id)))
            da_list.append(da_id)
            self._data[stop_id] = da_list
            # if count > 50: break

        f.close()

    def get_stop_das(self, stop_id):
        data = self._data.get(stop_id)
        if data is None:
            return None

        return data

    def get_da_pop(self, da_id):
        return self.da_centroids.get_population(da_id)

    def get_da_centroid(self, da_id):
        return self.da_centroids.get_centroid(da_id)

    def get_da_list(self):
        return self.da_centroids.get_da_id_list()


class Weight(object):

    def __init__(self):
        pass

    def butterworth(self, d, dpass, e, n):

        r = float(d)/float(dpass)
        rp = math.pow(r, n)
        result = 1.0 / math.sqrt(1.0 + e * rp)
        return result

class Runner2(object):

    def __init__(self):
        self._base_path = "../data/sts/csv/2018_05_04/"

    def run(self):

        stop_mgr = TransitStops(self._base_path)

        stop_ids = stop_mgr.get_ids()
        for stop_id in stop_ids:
            print stop_id

        stop_mgr.make_square_buffers()

class Runner(object):

    def __init__(self):

#        self._base_path = "../data/sts/csv/2018_06_21/
        self._base_path = "../data/sts/csv/2018_05_04/"
        self._service_type = SERVICE.MWF
        self._time_of_day = 8 * 60 * 60  # 8 AM

        self._stop_times = StopTimes(self._base_path)
        self._weight = Weight()
        self._intersect = Intersect()


    def test_departures(self):
        print "called"

        route_id_list = self._stop_times.get_route_ids()
        print "route count", len(route_id_list)
        stop_id_list = self._stop_times.get_stop_ids()
        print "stop list", len(stop_id_list)

        counts = {}
        test2 = {}

        for route_id in route_id_list:
            count = 0
            print "Route:", self._stop_times.get_route_name_from_id(route_id)

            for stop_id in stop_id_list:
                departures = self._stop_times.get_stop_route_departures(stop_id,route_id,0,SERVICE.MWF)
                # print departures
                count += len(departures)

#                if len(departures) > 0 and route_id in [10026, 10101]:
#                if len(departures) > 0 and route_id in [10073, 10148]:
                if len(departures) > 0 and route_id in [10152, 10077]:
                    data = test2.get(route_id, {})
                    data[stop_id] = len(departures)
                    test2[route_id] = data

            counts[route_id] = count

        s = []
        for k, v in counts.iteritems():
            s.append((self._stop_times.get_route_name_from_id(k), v, k))

        s = sorted(s)

        for item in s:
            print item[2], item[0], item[1]

        for route_id, data in test2.iteritems():
            print "Route ID", route_id
            for stop_id, departures in data.iteritems():
                print "  stop: %d departs: %d" % (stop_id, departures)



    def run(self):
        """

        """

        # This file was generated by ArcGIS for circular buffers around the bus stops
        # (to determine which DAs intersect with the bus stops)
        self._intersect.load("../data/DA_intersect_stop_circle_june.csv", expected_parts=32, stop_index=5, da_index=10)

        stop_ids = self._stop_times.get_stop_ids()

        # Demand at each stop is the first step in the 3sfca
        demand_dict = {}

        # loop through all the stops.
        for stop_id in stop_ids:
            stop_name = self._stop_times.get_stop_name(stop_id)

            print "Stop %d (%s)" % (stop_id, stop_name)

            # For each stop, compute the demand
            intersecting_das = self._intersect.get_stop_das(stop_id)

            data = {}

            sum_weight_pop = 0.0

            if intersecting_das is None:
                print "no intersecting DAs!!!!"
            else:
                for da_id in intersecting_das:
                    pop = self._intersect.get_da_pop(da_id)

                    stop_point = self._stop_times.get_stop_point(stop_id)
                    da_centroid = self._intersect.get_da_centroid(da_id)

                    dist = get_point_dist(stop_point, da_centroid)
                    # print dist

                    w = self._weight.butterworth(dist, 250, 1, 6)

                    data[da_id] = {
                        KEY.DISTANCE : dist,
                        KEY.POPULATION : pop,
                        KEY.WEIGHT : w
                    }

                    sum_weight_pop += (float(pop) * w)

                    print "    INTERSECTS: %d (pop. %d, dist %.2f weight: %0.3f)" % (da_id, pop, dist, w)

            print "    TOTAL SUM_WEIGHT_POP", sum_weight_pop
            #demand_dict[stop_id] = data
            # All we need to keep is the sum of the weighted population
            demand_dict[stop_id] = sum_weight_pop

        da_list = self._intersect.get_da_list()

        stop_dict = self.get_stops_for_da(da_list, stop_ids, mode="circular", radius=400)


        # TEST TEST TEST -----------------------

        # test_data = stop_dict.get(47110453)
        # for item in test_data:
        #     print item
        #
        #     stop_id = item[0]
        #     print "demand", demand_dict.get(stop_id)
        #
        # raise ValueError("temp_stop")

        # END TEST END TEST

        departure_dict = self.make_departure_dict(stop_dict)


        # # TEST TEST TEST
        # test_data = departure_dict.get(47110453)
        # print repr(test_data)
        #
        # for k, v in test_data.iteritems():
        #     print "KEY", k
        #     print "VALUE", v
        #     route_id = v.get(KEY.ROUTE_ID)
        #     route_name = self._stop_times.get_route_name_from_id(route_id)
        #     print "ROUTE NAME", route_name
        #
        # raise ValueError("temp stop")
        # # END TEST

        scores = self.compute_da_scores(demand_dict, departure_dict)

        f = open("da_score.csv", "w")
        f.write("FID,DAUID,score\n")

        index = 1
        max_score = 0
        for da_id, score in scores.iteritems():
            print "DAUID: %d score: %f" % (da_id, score)
            f.write("%d,%d,%f\n" % (index, da_id, score))
            index += 1
            if score > max_score:
                max_score = score
        f.close()

        print "done. max_score", max_score

    def compute_da_scores(self, demand_dict, departure_dict):

        #mode = 'est_wait_sec'
        mode = 'daily_departures'

        result = {}
        for da_id, da_data in departure_dict.iteritems():
            print "Compute Score for DA: %s" % repr(da_id)

            total_score = 0.0

            # Step one, for each departure (service) we must compute a demand score
            for k, v in da_data.iteritems():

                if mode == 'est_wait_sec':
                    est_wait_sec = v.get(KEY.EST_WAIT_SEC)
                    if est_wait_sec is None:
                        # Do not consider this departure
                        continue

                    service = (3600.0 - float(est_wait_sec)) / 3600.0
                    if service < 0:
                        print "no service"
                        continue
                elif mode == 'daily_departures':
                    service = v.get(KEY.DAILY_DEPARTURES)
                else:
                    raise ValueError("invalid mode")

                stop_id = v.get(KEY.STOP_ID)
                dist = v.get(KEY.DISTANCE)

                # print k, service

                demand = demand_dict.get(stop_id)
                # print "demand", repr(demand)
                if demand is None:
                    raise ValueError("No demand")

                if demand == 0.0:
                    print "WARN: Demand is 0!!!", stop_id
                    continue

                r = service / demand

                w = self._weight.butterworth(dist, 250, 1, 6)

                total_score += r * w

            result[da_id] = 1000 * total_score

        return result

    def make_departure_dict(self, stop_dict):
        """
        This method converts the "stops" to "departures".  There could be duplicate departures
        (ie at different stops) in which case we only keep closest departure
        """
        result = {}
        for da_id, stop_list in stop_dict.iteritems():

            data = {}

            print "DA_ID: %d" % da_id
            for item in stop_list:
                stop_id = item[0]
                stop_dist = item[1]

                departures = self._stop_times.get_stop_departures(stop_id, self._service_type)
                for departure in departures:
                    # print "stop_id: %d departure: %s" % (stop_id, repr(departure))
                    route_id = departure.get(KEY.ROUTE_ID)
                    direction = departure.get(KEY.DIRECTION)

                    depart_key = "%d-%d" % (route_id, direction)
                    if not data.has_key(depart_key):
                        # print "Found a new departure: %s" % repr(depart_key)
                        data[depart_key] = {
                            KEY.STOP_ID     : stop_id,
                            KEY.DISTANCE    : stop_dist,
                            KEY.ROUTE_ID    : route_id,
                            KEY.DIRECTION   : direction
                        }

                    else:
                        d = data.get(depart_key)
                        stop_id_d = d.get(KEY.STOP_ID)
                        stop_dist_d = d.get(KEY.DISTANCE)

                        if stop_id_d == stop_id:
                            # This is just another departure from the same stop
                            # print "same route/stop"
                            continue

                        if stop_dist < stop_dist_d:
                            # print "found same departure at closer stop!! %s: %d (%f) -> %d (%f)" % \
                            #     (depart_key, stop_id_d, stop_dist_d, stop_id, stop_dist)
                            data[depart_key] = {
                                KEY.STOP_ID     : stop_id,
                                KEY.DISTANCE    : stop_dist,
                                KEY.ROUTE_ID    : route_id,
                                KEY.DIRECTION   : direction
                            }

            # This loop determines estimated wait time for the filtered list of stops
            data2 = {}
            for k, v in data.iteritems():
                stop_id = v.get(KEY.STOP_ID)
                stop_dist = v.get(KEY.DISTANCE)
                route_id = v.get(KEY.ROUTE_ID)
                direction = v.get(KEY.DIRECTION)

                route_name = self._stop_times.get_route_name_from_id(route_id)
                stop_name = self._stop_times.get_stop_name(stop_id)

                departure_list = self._stop_times.get_stop_route_departures(stop_id, route_id, direction, self._service_type)
                estimated_wait_sec = self._stop_times.get_estimated_wait(stop_id, route_id, direction, self._service_type, self._time_of_day)

                v[KEY.EST_WAIT_SEC] = estimated_wait_sec
                v[KEY.DAILY_DEPARTURES] = len(departure_list)

                data2[k] = v
                print "K: %s Route: %s - Stop: %s (%d) dist: %.2f (departs: %d) wait: %s"  % \
                      (repr(k), route_name, stop_name, stop_id, stop_dist, len(departure_list), estimated_wait_sec)

            result[da_id] = data2

        return result

    def get_stops_for_da(self, da_ids, stop_ids, mode="Unknown", radius=None):
        """
        This method gets the stops near the da centriods.  It supports a variety
        of different methods
        """
        if mode == 'circular':
            result = self.get_stops_for_da_circular(da_ids, stop_ids, radius=radius)
        else:
            raise ValueError("mode not supported: %s" % mode)

        return result

    def get_stops_for_da_circular(self, da_ids, stop_ids, radius=None):

        result = {}

        for da_id in da_ids:

            da_centroid = self._intersect.get_da_centroid(da_id)
            stop_list = []

            # Loop through all stops, finding those within a 400m circular buffer
            for stop_id in stop_ids:
                stop_point = self._stop_times.get_stop_point(stop_id)
                dist = get_point_dist(stop_point, da_centroid)
                if dist < radius:
                    # print "Stop %d dist %f" % (stop_id, dist)
                    stop_list.append((stop_id, dist))

            result[da_id] = stop_list

        return result

    def test_filter(self):

        filter = Weight()
        for d in xrange(200):
            w = filter.butterworth(d*4 , 250, 1, 6)

            print "Dist: %d weight: %f" % (d * 4, w)

if __name__ == "__main__":

    # runner = Runner()
    # runner.run()

    runner = Runner2()
    runner.run()

    # runner.test_filter()
    # runner.test_departures()
