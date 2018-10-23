import os
import numpy as np
import simplejson

from da_manager import DaData
from geometry import Point
from geometry import Polygon
from geometry import Polypoint


from plotter import Plotter
from plotter import ATTR

from scipy.stats import pearsonr

class Walkscore(object):

    def __init__(self):

        self._items = []
        self._da_data = {}
        self.load_file()

    def load_file(self):

        counter = 0
        f = open("data/csv/walkscore.csv", "r")

        temp = {}

        for line in f:
            counter += 1
            if counter == 1: continue

            parts = line.split(",")
            postal_code = parts[1].strip()
            lat = float(parts[2].strip())
            lng = float(parts[3].strip())

            da_id = int(parts[4].strip())
            walkscore = int(parts[5].strip())

            self._items.append((lat, lng, walkscore))

            scores = temp.get(da_id, [])
            scores.append(walkscore)
            temp[da_id] = scores

        f.close()

        for da_id, scores in temp.iteritems():
            ave_score = np.mean(scores)
            self._da_data[da_id] = ave_score

    def get_points(self):
        return self._items

    def get_da_score(self, da_id):

        return self._da_data.get(da_id)

class Runner(object):

    def __init__(self):

        self._da_man = DaData()
        self.das = self._da_man.get_das()
        self._da_not_found = []
        self._walkman = Walkscore()

    def plot_scores(self):

        plotter = Plotter()

        points = self._walkman.get_points()

        for point in points:
            lat = point[0]
            lng = point[1]
            score = point[2]
            polypoint = Polypoint()
            polypoint.add_point(Point(lat, lng))

            opacity = float(score)/100.0
            polypoint.set_attribute(ATTR.FILL_OPACITY, opacity)
            polypoint.set_attribute(ATTR.FILL_COLOR, "#ff0000")
            polypoint.set_attribute(ATTR.RADIUS, 50)


            plotter.add_polypoint(polypoint)

        plotter.plot("temp/maps/walkscore.html")

    def plot_da_scores(self):

        plotter = Plotter()

        score_list = []

        for da in self.das:
            walkscore = self._walkman.get_da_score(da._da_id)
            print "walkscore", walkscore

            if walkscore is None:
                score_list.append((da.get_id(), 0.0))
                continue

            score_list.append((da.get_id(), walkscore))
            p = da.get_polygon()

            opacity = float(walkscore) / 100.0

            p.set_attribute(ATTR.FILL_COLOR, "#FF0000")
            p.set_attribute(ATTR.FILL_OPACITY, opacity*opacity)
            p.set_attribute(ATTR.STROKE_WEIGHT, 1)
            p.set_attribute(ATTR.STROKE_COLOR, "#202020")
            p.set_attribute(ATTR.STROKE_OPACITY, 1)
            plotter.add_polygon(p)

        plotter.plot("temp/maps/da_walkscore.html")


        other_scores = self._da_man.get_transit_percentages()

        print len(other_scores)
        print len(score_list)

        # print other_scores
        my_scores = sorted(score_list)

        my_sc = [item[1] for item in my_scores]
        other_sc = [item[1] for item in other_scores]

        result = pearsonr(my_sc, other_sc)
        print result

    def walkscore_to_csv(self):

        print "read walkscore files"

        files = os.listdir("walkscore")

        data = {}

        for file in files:
            # print file
            # print type(file)

            file_name = "walkscore/%s" % file
            f = open(file_name, "r")
            item = simplejson.load(f)
            f.close()

            for k, v in item.iteritems():
                # print k, v

                ws_link = item.get('ws_link')
                walkscore = item.get('walkscore')
                snapped_lat = item.get('snapped_lat')
                snapped_lng = item.get('snapped_lon')

                pos = ws_link.find("-SK-")
                postal_code = ws_link[pos+4:pos+11]
                postal_code = postal_code.replace('-', ' ')


                # print walkscore, snapped_lat, snapped_lng, postal_code
                # print type(snapped_lng), type(snapped_lat)

                item_data = data.get(postal_code, {})
                key = "%s%s" % (repr(snapped_lat), repr(snapped_lng))
                # print key
                item_data[key] = (snapped_lat, snapped_lng, walkscore)
                data[postal_code] = item_data

        f = open("data/csv/walkscore.csv", "w")

        f.write("index,postal_code,lat,lng,walkscore,da_id\n")

        index = 0
        for postal_code, value in data.iteritems():
            print postal_code, value
            for item in value.itervalues():
                lat = item[0]
                lng = item[1]
                walkscore = item[2]


                point = Point(lat, lng)

                da_id = 0
                test_count =0

                for da in self.das:
                    if point.within(da.get_polygon()):
                        # print "Point in DA", da.get_id()
                        test_count += 1
                        da_id = da.get_id()

                if test_count != 1:
                    self._da_not_found.append(item)
                    continue

                f.write("%d,%s,%f,%f,%d,%d\n" % (index, postal_code, lat, lng, da_id, walkscore))
                index += 1

        f.close()


        print self._da_not_found


if __name__ == "__main__":

    runner = Runner()
    # runner.walkscore_to_csv()
    # runner.plot_scores()
    runner.plot_da_scores()
