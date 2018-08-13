import math

from my_utils import Filter
from stop_times import StopTimes
from stop_times import SERVICE
from stop_times import KEY

DECAY = Filter()

class Score(object):

    # def __init__(self, base_path, stops=None):
    #
    #     self._base_path = base_path
    #     self._stops = stops
    #     self._brt_mode = False
    #
    #     if base_path.find("2018_05_04") > 0:
    #         print "this is the JUNE data"
    #
    #     elif base_path.find('2018_08_05') > 0:
    #         print "this is the JULY data"
    #
    #     else:
    #         self._brt_mode = True
    #
    #     if not self._brt_mode:
    #         self._stop_times = StopTimes(self._base_path, stops=stops)

    def __init__(self):
        pass

    def get_score_simple(self, raster, stop_tuples):

        score = 0
        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        info = {}

        for item in stop_tuples:
            stop_id = item[1]
            stop_p = item[0]
            stop = item[2]

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if raster_p.intersects(stop_p):
                demand = stop.get_demand()
                a = 1.0 / float(demand)
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
