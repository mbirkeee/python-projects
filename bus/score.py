import math

from my_utils import Filter
from stop_times import StopTimes
from stop_times import SERVICE
from stop_times import KEY

from modes import SCORE_METHOD
from modes import DECAY_METHOD

# DECAY = Filter()

class Score(object):

    def __init__(self, dataman):
        self._dataman = dataman
        self._filter = Filter(dpass=250)
        self._nearest_only = None
        self._decay_method = None
        self._time_str = None
        self._service = None
        self._method = None

    def set_method(self, value):
        self._method = value

    def set_service(self, value):
        self._service = value

    def set_time_str(self, value):
        self._time_str = value

    def set_nearest_only(self, value):
        self._nearest_only = value

    def set_decay_method(self, value):
        self._decay_method = value

    def get_decay_factor(self, point1, point2, decay_method):

        if decay_method in [None, DECAY_METHOD.CROW_100, DECAY_METHOD.CROW_250]:
            distance = point1.get_distance(point2, method="crow")

        elif decay_method in [DECAY_METHOD.GRID_250]:
            distance = point1.get_distance(point2, method="grid")

        else:
            raise ValueError("decay method not supported: %s" % repr(decay_method))

        if decay_method == None:
            decay = 1.0

        elif decay_method in [DECAY_METHOD.CROW_250, DECAY_METHOD.GRID_250]:
            self._filter.set_dpass(250)
            decay = self._filter.butterworth(distance)

        elif decay_method == DECAY_METHOD.CROW_100:
            self._filter.set_dpass(100)
            decay = self._filter.butterworth(distance)

        else:
            raise ValueError("decay method not supported: %s" % repr(decay_method))

        return distance, decay

    def get_score(self, raster, stop_tuples):
        if self._method in [
            SCORE_METHOD.DEPARTURES_PER_HOUR,
            SCORE_METHOD.DEPARTURES_PER_DAY,
            SCORE_METHOD.DEPARTURES_PER_WEEK]:

            score = self.get_score_departures(raster, stop_tuples)

        elif self._method == SCORE_METHOD.STOP_COUNT:
            score = self.get_score_stop_count(raster, stop_tuples)

        elif self._method == SCORE_METHOD.DIST_TO_CLOSEST_STOP:
            score = self.get_score_closest_stop(raster, dist_method)

        else:
            raise ValueError("Score method not supported: %s" % self._method)

        return score

    def get_closest(self, items, key):

        result = None
        closest = None

        for item in items:
            distance = item.get(KEY.DISTANCE)
            if closest is None or distance < closest:
                closest = distance
                result = item

        print "KEY: %s Closest: %s" % (repr(key), repr(closest))

        # Loop for debugging
        # for item in items:
        #     if item == result:
        #         continue
        #     distance = item.get(KEY.DISTANCE)
        #     print "Punted farther dist: %s" % repr(distance), key

        return result

    def get_score_closest_stop(self, raster, distance_method):

        active_stops = self._dataman.get_active_stops()
        min_dist, min_stop = raster.get_closest_stop(active_stops, method=distance_method)
        return min_dist

    def get_score_departures(self, raster, stop_tuples):

        print "RASTER--------", raster.get_id()
        total_score = 0.0
        debug_me = False

        depart_dict = {}

        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        # This loop is just for debugging
        if debug_me:
            for item in stop_tuples:
                stop_p = item[0]
                stop_id = item[1]
                stop = self._dataman.get_stop(stop_id)

                # Does the raster polygon intersect the stop polygon?
                # TODO: isn't this a given base on the passed in intersecting polygons?
                if not raster_p.intersects(stop_p):
                    continue

                distance, decay_factor = self.get_decay_factor(stop.get_point(), raster_point, self._decay_method)
                print "stop: %d distance: %f decay: %f" % (stop_id, distance, decay_factor)

            print "^^^^^^^^^^^^^^^^^^^^^^^^^"


        for item in stop_tuples:
            stop_p = item[0]
            stop_id = item[1]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if not raster_p.intersects(stop_p):
                # The intersections are for the DAs and stops, not the rasters.
                continue

            distance, decay_factor = self.get_decay_factor(stop.get_point(), raster_point, self._decay_method)

            route_ids = stop.get_route_ids()
            for route_id in route_ids:
                print "Stop %d serves route: %d" % (stop_id, route_id)

                for direction in [0, 1]:
                    if self._method == SCORE_METHOD.DEPARTURES_PER_HOUR:
                        departs = self._dataman.get_departs_per_hour(route_id, direction, stop_id, self._service, self._time_str)
                    elif self._method == SCORE_METHOD.DEPARTURES_PER_DAY:
                        departs = self._dataman.get_departs_per_day(route_id, direction, stop_id, self._service)
                    elif self._method == SCORE_METHOD.DEPARTURES_PER_HOUR:
                        departs = self._dataman.get_departs_per_week(route_id, direction, stop_id)
                    else:
                        raise ValueError("depart method %s not supported" % repr(depart_method))

                    if departs is None or departs == 0:
                        continue

                    if departs > 6.0:
                        print "*"*80

                    print "Route ID: %d Stop ID: %d :Departures: %f" % (route_id, stop_id, departs)

                    # Make a list of unique departures so that closest stop can be determined
                    key = "%d-%d" % (route_id, direction)
                    stop_list = depart_dict.get(key, [])
                    stop_list.append({
                        KEY.STOP_ID         : stop_id,
                        KEY.DEPARTURES      : departs,
                        KEY.DISTANCE        : distance,
                        KEY.DECAY_FACTOR    : decay_factor
                    })
                    depart_dict[key] = stop_list

        # Second pass.. Loop through all the results to filter out more distant ones
        for key, items in depart_dict.iteritems():
            if self._nearest_only:
                items = [self.get_closest(items, key)]

            for item in items:
                departs = item.get(KEY.DEPARTURES)
                decay_factor = item.get(KEY.DECAY_FACTOR)

                total_score += departs * decay_factor

        print "COMPUTED SCORE", total_score
        return total_score


    def get_score_stop_count_with_decay(self, raster, stop_tuples):

        score = 0
        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        for item in stop_tuples:
            stop_p = item[0]
            stop_id = item[1]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if raster_p.intersects(stop_p):
                a = 1.0

                distance = raster_point.get_distance(stop.get_point())
                # # print "the distance is", distance
                a = a * DECAY.butterworth(distance)

                score += a

        return score

    def get_score_stop_count(self, raster, stop_tuples):

        if self._decay_method is not None:
            raise ValueError("decay method not supported")

        score = 0
        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        for item in stop_tuples:
            stop_id = item[1]
            stop_p = item[0]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if raster_p.intersects(stop_p):
                a = 1.0
                score += a

        return score
