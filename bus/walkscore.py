import os
import simplejson
from da_manager import DaData
from geometry import Point
from geometry import Polygon

class Runner(object):

    def __init__(self):

        self._da_man = DaData()
        self.das = self._da_man.get_das()
        self._da_not_found = []
        print "here"

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
    runner.walkscore_to_csv()
