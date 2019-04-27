import math

from my_utils import Filter
from my_utils import get_butterworth_decay

from stop_times import KEY
from modes import SCORE_METHOD
from modes import DEMAND_METHOD

from butterworth import wait_decay
from walkscore import WalkscoreDecay

from scipy import stats

class Score(object):

    def __init__(self, dataman, mode_man):
        self._dataman = dataman
        self._mode_man = mode_man

        self._filter = Filter(dpass=250)
        self._wait_decay_normalize_value = None # Computed on demand
        self._walkscore_decay = WalkscoreDecay()

    def get_decay_factor(self, point1, point2, decay_method):

        if decay_method is None:
            distance = point1.get_distance(point2, method="crow")
            return distance, 1.0

        parts = decay_method.split('_')
        method = parts[0].strip().lower()

        dpass = int(parts[1].strip())

        if method == 'grid':
            distance = point1.get_distance(point2, method="grid")
        elif method == 'crow':
            distance = point1.get_distance(point2, method="crow")
        elif method == 'exp':
            distance = point1.get_distance(point2, method="grid")

        else:
            raise ValueError("invalid method: %s" % method)

        if dpass == 99999:
            decay = self._walkscore_decay.get_decay(distance)
        else:
            self._filter.set_dpass(dpass)
            if method in ['grid', 'crow']:
                decay = self._filter.butterworth(distance)
            else:
                decay = self._filter.exp(distance)


        return distance, decay

    def get_score(self, raster, stop_tuples):

        method = self._mode_man.get_score_method()

        if method in [
            SCORE_METHOD.DEPARTURES_PER_HOUR,
            SCORE_METHOD.DEPARTURES_PER_DAY,
            SCORE_METHOD.DEPARTURES_PER_WEEK,
            SCORE_METHOD.DECAYED_WAIT]:

            score = self.get_score_departures(raster, stop_tuples)

        elif method == SCORE_METHOD.STOP_COUNT:
            score = self.get_score_stop_count(raster, stop_tuples)

        elif method == SCORE_METHOD.COVERAGE:
            score = self.get_score_coverage(raster, stop_tuples)

        elif method == SCORE_METHOD.DIST_TO_CLOSEST_STOP:
            dist_method = self._mode_man.get_distance_method()
            score = self.get_score_closest_stop(raster, dist_method)

        else:
            raise ValueError("Score method not supported: %s" % method)

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

        score_method = self._mode_man.get_score_method()
        decay_method = self._mode_man.get_distance_decay()
        service_type = self._mode_man.get_service_type()
        normalize_value = self._mode_man.get_normalize_value()
        service_time = self._mode_man.get_service_time()
        stop_demand = self._mode_man.get_stop_demand()

        print "*"*80

        for item in stop_tuples:
            stop_p = item[0]
            stop_id = item[1]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if not raster_p.intersects(stop_p):
                # The intersections are for the DAs and stops, not the rasters.
                continue

            distance, decay_factor = self.get_decay_factor(stop.get_point(), raster_point, decay_method)

            # print "--> DISTANCE", distance, "DECAY_FACTOR", decay_factor

            route_ids = stop.get_route_ids()
            for route_id in route_ids:
                print "Stop %d serves route: %d ------ " % (stop_id, route_id)

                for direction in [0, 1]:
                    if score_method == SCORE_METHOD.DEPARTURES_PER_HOUR:
                        departs = self._dataman.get_departs_per_hour(route_id, direction, stop_id, service_type, service_time)
                        if departs is not None and normalize_value is not None:
                            departs = departs / normalize_value

                    elif score_method == SCORE_METHOD.DEPARTURES_PER_DAY:
                        departs = self._dataman.get_departs_per_day(route_id, direction, stop_id, service_type)

                    elif score_method == SCORE_METHOD.DEPARTURES_PER_WEEK:
                        departs = self._dataman.get_departs_per_week(route_id, direction, stop_id)

                    elif score_method == SCORE_METHOD.DECAYED_WAIT:
                        departs = self.get_score_decayed_wait(route_id, direction, stop_id)

                    else:
                        raise ValueError("Score method %s not supported" % repr(score_method))

                    if departs is None or departs == 0:
                        continue

                    old_departs = departs

                    # Apply stop demand if required
                    if stop_demand is not None:
                        demand = stop.get_demand()
                        demand_method = self._mode_man.get_demand_method()

                        if demand_method == DEMAND_METHOD.DIVIDE:
                            if demand < 1.0:
                                demand = 1.0
                            departs = departs / demand
                        else:
                            parts = demand_method.split("_")
                            if parts[0].strip() == 'pow':
                                power = float(parts[1])
                                departs = departs * math.pow(demand, power)

                            else:
                                departs = None

                        if departs is None:
                            raise ValueError("invalid demand method")

                    print "Route ID: %d Stop ID: %d DIR: %d Departures: %f" % \
                          (route_id, stop_id, direction, old_departs)

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
        nearest_only = self._mode_man.get_nearest_only()

        for key, items in depart_dict.iteritems():
            if nearest_only:
                items = [self.get_closest(items, key)]

            for item in items:
                departs = item.get(KEY.DEPARTURES)
                decay_factor = item.get(KEY.DECAY_FACTOR)

                total_score += departs * decay_factor

        print "COMPUTED SCORE", total_score
        return total_score

    def get_score_decayed_wait(self, route_id, direction, stop_id):

        service_type = self._mode_man.get_service_type()
        wait_bandpass = self._mode_man.get_wait_bandpass()
        service_time = self._mode_man.get_service_time()
        # print "THIS IS THE SERVICE TIME", service_time

        departs_per_hour = self._dataman.get_departs_per_hour(route_id, direction, stop_id, service_type, service_time)
        # print "departs per hour", departs_per_hour
        if not departs_per_hour:
            return

        if self._wait_decay_normalize_value is None:
            normalize_value = self._mode_man.get_normalize_value()
            self._wait_decay_normalize_value = wait_decay(normalize_value, wait_bandpass)

        decay = wait_decay(departs_per_hour, wait_bandpass)
        normalized_decay = decay / self._wait_decay_normalize_value

        return normalized_decay


    def get_score_coverage(self, raster, stop_tuples):

        # if self._decay_method is not None:
        #     raise ValueError("decay method not supported")

        # score = get_score_departures(raster, stop_tuples)

        depart_dict = {}

        total_score = 0.0
        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        for item in stop_tuples:
            stop_p = item[0]
            stop_id = item[1]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if not raster_p.intersects(stop_p):
                # The intersections are for the DAs and stops, not the rasters.
                continue

            decay_method = self._mode_man.get_distance_decay()
            distance, decay_factor = self.get_decay_factor(stop.get_point(), raster_point, decay_method)

            print "DISTANCE", distance, "DECAY_FACTOR", decay_factor

            route_ids = stop.get_route_ids()
            for route_id in route_ids:
                print "Stop %d serves route: %d" % (stop_id, route_id)

                for direction in [0, 1]:
                    departs = self._dataman.get_departs_per_week(route_id, direction, stop_id)

                    if departs is None or departs == 0:
                        continue

                    # Because we are just counting coverage, any number of deparutes counts as 1
                    departs = 1

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
        nearest_only = self._mode_man.get_nearest_only()

        for key, items in depart_dict.iteritems():
            if nearest_only:
                items = [self.get_closest(items, key)]

            for item in items:
                departs = item.get(KEY.DEPARTURES)
                decay_factor = item.get(KEY.DECAY_FACTOR)

                total_score += departs * decay_factor

        print "COMPUTED SCORE", total_score
        return total_score


        # for item in stop_tuples:
        #     stop_id = item[1]
        #     stop_p = item[0]
        #     stop = self._dataman.get_stop(stop_id)
        #
        #     if stop_id != stop.get_id():
        #         raise ValueError("fixme")
        #
        #     if not raster_p.intersects(stop_p): continue
        #
        #     if self._mode_man.get_nearest_only():
        #         raise ValueError("Must implement nearest only")
        #
        #     distance_decay_method = self._mode_man.get_distance_decay()
        #
        #     if distance_decay_method != None:
        #         distance_decay = get_butterworth_decay(distance_decay_method, stop.get_point(), raster_point)
        #         print "DISTANCE DECAY: %f" % distance_decay
        #     else:
        #         distance_decay = 1.0
        #
        #     route_ids = stop.get_route_ids()
        #     route_count = len(route_ids)
        #
        #     for route in route_ids:

            #
            # print "THIS STOP SERVES %d routes", route_count
            #
            # a = distance_decay * route_count
            # score += a

        return score

    def get_score_stop_count(self, raster, stop_tuples):

        # if self._decay_method is not None:
        #     raise ValueError("decay method not supported")

        score = 0
        raster_p = raster.get_polygon()
        raster_point = raster_p.get_centroid()

        for item in stop_tuples:
            stop_id = item[1]
            stop_p = item[0]
            stop = self._dataman.get_stop(stop_id)

            if stop_id != stop.get_id():
                raise ValueError("fixme")

            if not raster_p.intersects(stop_p): continue

            distance_decay_method = self._mode_man.get_distance_decay()
            if distance_decay_method != None:
                distance_decay = get_butterworth_decay(distance_decay_method, stop.get_point(), raster_point)
                print "DISTANCE DECAY: %f" % distance_decay
            else:
                distance_decay = 1.0

            a = distance_decay
            score += a

        return score


class ScoreManager2(object):

    def __init__(self):

        self._data = None
        self._score_tuples = []
        self._max_score = None
        self._min_score = None

    def reset(self):
        self._data = None
        self._score_tuples = []
        self._max_score = None
        self._min_score = None

    def add_score(self, thing, score):
        self._score_tuples.append((thing, score))

    def get_sorted_scores(self, reverse=False):

        scores = [item[1] for item in self._score_tuples]

        scores = sorted(scores)
        if reverse:
            scores.reverse()

        return scores

    def get_clipping_score_from_percent(self, clip_percent):

        score_count = float(len(self._score_tuples))

        scores = self.get_sorted_scores(reverse=True)

        clip_count = 0

        clipping_score = None
        for i, score in enumerate(scores):
            percentage = 100.0 * (float(i)/score_count)
            if percentage > clip_percent:
                break
            clipping_score = score
            clip_count += 1
            # print i, percentage, score, clipping_score

        return clipping_score, clip_count

    def compute_max_score(self):
        max_score = None
        for item in self._score_tuples:
            score = item[1]

            if max_score is None or score > max_score:
                max_score = score

        self._max_score = max_score
        return self._max_score

    def get_clipping_score_from_max(self, clip_level):

        score_count = float(len(self._score_tuples))

        if self._max_score is None:
            self.compute_max_score()

        clip_score = clip_level * self._max_score
        clip_count = 0
        for item in self._score_tuples:
            score = item[1]
            if score > clip_score:
                clip_count += 1

        return clip_score, clip_count

    def get_clipping_score(self, clip):

        if clip == "log":
            return "log", 0

        if clip is None:
            if self._max_score is None:
                self.compute_max_score()
            return self._max_score, 0

        if isinstance(clip, float):
            return self.get_clipping_score_from_max(clip)
        elif isinstance(clip, str):
            parts = clip.split("_")
            value = float(parts[1].strip())
            kind = parts[0].strip()
            if kind == "percent":
                return self.get_clipping_score_from_percent(value)
            elif kind == "fraction":
                return self.get_clipping_score_from_max(value)

        raise ValueError("error getting clip score")


class ScoreManager(object):
    """
    This class accepts a list of items and their scores.  It computes the
    min/max, zscores, and can return raw values or as a percentage of min/max.
    It can clip outliers, etc.
    """
    def __init__(self, score_tuples):

        self._score_tuples = score_tuples

        self._raw_data = {}

        self._max_score = None
        self._min_score = None

        self._max_z_score = None
        self._min_z_score = None

        self._max_log_score = None
        self._min_log_score = None

        self._color_cold        = "#0000ff"
        self._color_hot         = "#ff0000"
        self._color_clipped     = "#fff240"

        self._clip_level = 1.0

        for item in score_tuples:
            thing = item[0]
            score = float(item[1])

            if self._max_score is None or score > self._max_score:
                self._max_score = score

            if self._min_score is None or score < self._min_score:
                self._min_score = score

            # Save the score in a dict keyed by the thing
            self._raw_data[thing] = {'score' : score }

        self._make_z_scores()
        self._make_log_scores()

        # for v in self._raw_data.itervalues():
        #     print repr(v)

        # raise ValueError('temp stop')

    def _make_log_scores(self):

        for i, item in enumerate(self._score_tuples):
            thing = item[0]
            score = item[1]
            log_score = math.log10(score+ 1.0)

            data = self._raw_data.get(thing)
            data['log_score'] = log_score
            self._raw_data[thing] = data

            if self._max_log_score is None or log_score > self._max_log_score:
                self._max_log_score = log_score

            if self._min_log_score is None or log_score < self._min_log_score:
                self._min_log_score = log_score

    def _make_z_scores(self):

        score_list = []
        for i, item in enumerate(self._score_tuples):
            score = item[1]
            score_list.append(score)

        z_scores = stats.zscore(score_list)

        for i, item in enumerate(self._score_tuples):
            thing = item[0]
            z_score = z_scores[i]

            if self._max_z_score is None or z_score > self._max_z_score:
                self._max_z_score = z_score

            if self._min_z_score is None or z_score < self._min_z_score:
                self._min_z_score = z_score

            data = self._raw_data.get(thing)
            data['z_score'] = z_score
            self._raw_data[thing] = data

        # # -- The section shifts scores up so all are +ve
        # self._max_z_score += abs(self._min_z_score)
        #
        # for thing, data in self._raw_data.iteritems():
        #     z_score = data.get('z_score')
        #     z_score += abs(self._min_z_score)
        #     data['z_score'] = z_score
        #
        #     score = data.get('score')
        #     ratio = score / z_score
        #
        #     # print "SCORE: %f ZSCORE: %f %f" % (score, z_score, ratio)
        #
        # self._min_z_score = 0
        # -- End section shift up --

        # raise ValueError('temp stop')

    def set_clip_level(self, clip_level, clip_color="#fff240"):
        self._clip_level = clip_level
        self._color_clipped = clip_color

    def get_z_score(self, thing, opacity=False):

        data = self._raw_data.get(thing)
        score = data.get('z_score')

        # print "GET ZSCORE COLOR CALLED", score

        if score > 0:
            level = score / self._max_z_score
            color = self._color_hot
            return level, self._color_hot
        else:
            level = score / self._min_z_score
            return level, self._color_cold

        color = self._color_hot
        level = score / self._max_z_score

        if level > self._clip_level:
            color = self._color_clipped
            level = 1.0
        else:
            level = level / self._clip_level

        if opacity:
            score = level

        return score, color

    def get_log_score(self, thing, opacity=False):

        data = self._raw_data.get(thing)
        score = data.get('log_score')

        color = self._color_hot
        level = score / self._max_log_score

        if level > self._clip_level:
            color = self._color_clipped
            level = 1.0
        else:
            level = level / self._clip_level

        if opacity:
            score = level

        return score, color

    def get_plot_color(self, thing, opacity=False, z_score=False, log_score=False):

        if log_score:
            return self.get_log_score(thing, opacity=opacity)

        if z_score:
            return self.get_z_score(thing, opacity=opacity)

        data = self._raw_data.get(thing)
        score = data.get('score')

        color = self._color_hot

        if self._min_score >= 0:
            range = self._max_score - self._min_score
            level = ( score - self._min_score ) / range
        else:
            raise ValueError("Cant yet handle score < 0")




        # if level > self._clip_level:
        #     color = self._color_clipped
        #     level = 1.0
        # else:
        #     level = level / self._clip_level

        if opacity:
            score = level

        return score, color


