from my_utils import DaCentriods
from my_utils import TransitData
from my_utils import get_dist
import math

class Intersect(object):

    def __init__(self):
        self._data = {}

        self.da_centroids = DaCentriods()

    def load(self, file_name, expected_parts, stop_index, da_index):

        count = 0
        f = open(file_name, 'r')
        for line in f:
            count += 1
            if count == 1: continue

            line = line.strip()
            parts = line.split(',')
            # print len(parts)
            if len(parts) != expected_parts:
                raise ValueError("Unexpected umber of parts")

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

    def get_da_utm(self, da_id):
        return self.da_centroids.get_utm(da_id)

class Weight(object):

    def __init__(self):
        pass

    def butterworth(self, d, dpass, e, n):

        r = float(d)/float(dpass)
        rp = math.pow(r, n)
        result = 1.0 / math.sqrt(1.0 + e * rp)
        return result


class Runner(object):

    def __init__(self):
        pass

    def run(self):
        """

        """

        weight = Weight()
        intersect = Intersect()
        intersect.load("../data/DA_intersect_stop_circle_june.csv", 32, 5, 10)

        transit_data = TransitData()
        transit_data.load_stops_from_csv("../data/sts/csv/2018_05_04/my-TransitStops.csv")

        stop_ids = transit_data.get_stop_id_list()

        for stop_id in stop_ids:
            print "Stop %d (%s)" % (stop_id, transit_data.get_stop_name(stop_id))

            intersecting_das = intersect.get_stop_das(stop_id)
            for da_id in intersecting_das:
                pop = intersect.get_da_pop(da_id)

                stop_utm = transit_data.get_stop_utm(stop_id)
                # print stop_utm
                da_utm = intersect.get_da_utm(da_id)
                # print da_utm
                dist = get_dist(stop_utm, da_utm)
                # print dist

                w = weight.butterworth(dist, 250, 1, 6)

                print "    INTERSECTS: %d (pop. %d, dist %.2f weight: %0.3f)" % (da_id, pop, dist, w)

if __name__ == "__main__":

    runner = Runner()
    runner.run()
