import math

from my_utils import Filter
from stop_times import StopTimes
from stop_times import SERVICE
from stop_times import KEY

from modes import DECAY_METHOD

# DECAY = Filter()

class Score(object):

    def __init__(self, dataman):
        self._dataman = dataman
        self._filter = Filter(dpass=250)

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

    def get_score_departures_per_hour(self, raster, stop_tuples, service, time_str, decay_method, nearest_only):

        print "RASTER--------", raster.get_id()
        total_departs = 0.0

        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        for item in stop_tuples:
            stop_p = item[0]
            stop_id = item[1]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if not raster_p.intersects(stop_p):
                continue

            decay_factor = self.get_decay_factor(stop.get_point(), raster_point, decay_method)

            route_ids = stop.get_route_ids()
            for route_id in route_ids:
                print "Stop serves route: %d" % route_id

                departs_per_hour_0 = self._dataman.get_departs_per_hour(route_id, 0, stop_id, service, time_str)
                departs_per_hour_1 = self._dataman.get_departs_per_hour(route_id, 1, stop_id, service, time_str)

                if departs_per_hour_0 is not None:
                    print "departures 0", departs_per_hour_0, decay_factor
                    total_departs += decay_factor * departs_per_hour_0

                if departs_per_hour_1 is not None:
                    print "departures 1", departs_per_hour_1, decay_factor
                    total_departs += decay_factor * departs_per_hour_1

        print "total departures", total_departs
        return total_departs

    def get_closest(self, items):

        result = None
        closest = None

        for item in items:
            distance = item.get(KEY.DISTANCE)
            if closest is None or distance < closest:
                closest = distance
                result = item

        return result

    def get_score_closest_stop(self, raster, distance_method):

        active_stops = self._dataman.get_active_stops()
        min_dist, min_stop = raster.get_closest_stop(active_stops, method=distance_method)
        return min_dist

    def get_score_departures_per_day(self, raster, stop_tuples, service, decay_method, nearest_only):

        print "RASTER--------", raster.get_id()
        total_score = 0.0

        route_dict = {}

        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        for item in stop_tuples:
            stop_p = item[0]
            stop_id = item[1]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            # Does the raster polygon intersect the stop polygon?
            # TODO: isn't this a given base on the passed in intersecting polygons?
            if not raster_p.intersects(stop_p):
                continue

            distance, decay_factor = self.get_decay_factor(stop.get_point(), raster_point, decay_method)

            route_ids = stop.get_route_ids()
            for route_id in route_ids:
                print "Stop %d serves route: %d" % (stop_id, route_id)

                for direction in [0, 1]:
                    departs = self._dataman.get_departs_per_day(route_id, direction, stop_id, service)

                    if departs is None or departs == 0:
                        continue

                    # Make a list of unique departures so that closest stop can be determined
                    key = "%d-%d" % (route_id, direction)
                    stop_list = route_dict.get(key, [])
                    stop_list.append({
                        KEY.STOP_ID         : stop_id,
                        KEY.DEPARTURES      : departs,
                        KEY.DISTANCE        : distance,
                        KEY.DECAY_FACTOR    : decay_factor
                    })
                    route_dict[key] = stop_list

            for key, items in route_dict.iteritems():
                if nearest_only:
                    items = [self.get_closest(items)]

                for item in items:
                    departs = item.get(KEY.DEPARTURES)
                    decay_factor = item.get(KEY.DECAY_FACTOR)

                    total_score += departs * decay_factor

        print "total departures", total_score
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

    def get_score_stop_count(self, raster, stop_tuples, decay_method):

        if decay_method is not None:
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

    def get_score(self, raster_p, stop_polygons):
        """
        This function considers the distance and stop demand, but not the service
        """
        score = 0

        raster_point = raster_p.get_centroid()

        info = {}

        for item in stop_polygons:
            stop_id = item[1]
            stop_p = item[0]

            if raster_p.intersects(stop_p):

                demand = self._stops.get_demand(stop_id)
                stop_point = self._stops.get_point(stop_id)

                service = self._stop_times.get_stop_departures(stop_id, SERVICE.MWF)

                for departure in service:
                    route_id = departure.get(KEY.ROUTE_ID)
                    direction = departure.get(KEY.DIRECTION)
                    distance = raster_point.get_distance(stop_point)

                    # print "Stop:", stop_id, "Route:", route_id, "dir", direction

                    key = "%s-%d" % (repr(route_id), direction)
                    data = info.get(key, {})

                    replace = False
                    have_dist = data.get('distance')
                    if have_dist:
                        if distance < have_dist:
                            replace = True
                            print "REPLACE EEXISTING DEPARTURE WITH CLOSER STOP!!!!", have_dist, distance, route_id, direction
                        else:
                            have_stop_id = data.get('stop_id')
                            if have_stop_id and have_stop_id == stop_id:
                                depart_count = data.get('count')
                                depart_count += 1
                                data['count'] = depart_count
                                info[key] = data
                    else:
                        replace = True

                    if replace:
                        info[key] = {
                            'stop_id' : stop_id,
                            'route_id' : route_id,
                            'distance' : distance,
                            'count' : 1,
                            'demand' : demand
                        }
        score = 0

        for k, v in info.iteritems():

            # print k, repr(v)

            # a = 1000 * v.get('count') / v.get('demand')
            # a = 100 * v.get('count') / math.log10(v.get('demand'))
            a = 10 * v.get('count')
            # a = 100 / v.get('demand')

            # See if we can detect an artificial increase in frequenct on route 10089
    #        if v.get('route_id') == 10089:
    #            a *= 2

            a = a * DECAY.butterworth(v.get('distance'))
            score += a

        return score
