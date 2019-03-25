import time
import simplejson
import os
import scandir
import urllib2
import urllib

from password import WALKSCORE_API_DR_BREE
from password import WALKSCORE_API_SPADINA_MEDICAL
from da_manager import DaData

class ExceptionDone(Exception):
    pass

class Runner(object):
    """
    Fetch the transit score by raster
    """
    def __init__(self):

        self._fetch_count = 0
        self._exists_count = 0
        self._daman = DaData()

        self._exists_count = 0
        self._fetch_count = 0
        self._stop_after = 1000

    def run(self):

        try:
            das = self._daman.get_das()
            for da in das:
                da_id = da.get_id()
                rasters = da.get_rasters(100)
                for raster in rasters:
                    # print raster
                    centroid = raster.get_centroid()
                    raster_id = raster.get_id()
                    print raster_id

                    lat = centroid.get_lat()
                    centroid.get_lng()
                    self.fetch(da_id, raster_id, centroid.get_lat(), centroid.get_lng())

                    if self._fetch_count >= self._stop_after:
                        print "Got max results (%d)... terminating" % self._stop_after
                        raise ExceptionDone

        except ExceptionDone:
            pass

        print "Fetched: %d" % self._fetch_count
        print "Exists count: %d" % self._exists_count

    def fetch(self, da_id, raster_id, lat, lng):
        print "FETCH:", da_id, raster_id, lat, lng
        # self._fetch_count += 1
        # return True

        target_file = "temp/transit_score/%d_%d.txt" % (da_id, raster_id)
        print target_file

        if os.path.isfile(target_file):
            print "File exists: %s, skipping..." % target_file
            self._exists_count += 1
            return False

        api_key = WALKSCORE_API_DR_BREE

        # api_key = WALKSCORE_API_SPADINA_MEDICAL

        # base = "http://api.walkscore.com/score?format=json&"
        #
        # q = {
        #     'address' : "Saskatoon SK %s" % postal_code,
        #     'transit': 1,
        #     'bike': 1,
        #     'lat' : lat,
        #     'lon' : lng,
        #     'wsapikey' : api_key
        # }

        # http://transit.walkscore.com/transit/score/?lat=47.6101359&lon=-122.3420567&city=Seattle&state=WA&wsapikey=your_key
        # http://transit.walkscore.com/transit/score/?lat=52.123011&city=Saskatoon&state=SK&lon=-106.652805&wsapikey=cbfda2f973cc7409fdb64499639e45760
        # base = "http://transit.walkscore.com/transit/score/?lat=47.6101359&lon=-122.3420567&city=Seattle&state=WA&"
        # base = "http://transit.walkscore.com/transit/supported/cities/?"

        base = "http://transit.walkscore.com/transit/score/?"

        q = {
        #    'address' : "Saskatoon SK %s" % postal_code,
        #    'transit': 1,
            'city' : "Saskatoon",
            'country' : "CA",
          #  'bike': 1,
            'lat' : lat,
            'lon' : lng,
            'wsapikey' : api_key
        }

        url = base + urllib.urlencode(q)

        print url

        response = urllib2.urlopen(url)
        result = response.read()
        response.close()
        print result

        if len(result) < 100:
            raise ValueError("bad data")

        thing = simplejson.loads(result)

        f = open(target_file, "w")
        simplejson.dump(thing, f, indent=4, sort_keys=True)
        f.close()

        self._fetch_count += 1

        print "TOTAL RESULTS: %d" % (self._exists_count + self._fetch_count)
        time.sleep(1)


    # def get_json_files(self, table):
    #     result = []
    #     path = os.path.join(self._json_path, table)
    #     for item in scandir.scandir(path):
    #
    #         if not item.is_file():
    #             print "skipping item"
    #             continue
    #
    #         print item.path
    #
    #         if not item.path.endswith(".json"):
    #             print "skipping file", item.path
    #             continue
    #
    #         result.append(item.path)
    #
    #     return result
    #
    # def get_items(self, file):
    #
    #     f = open(file, "r")
    #     data = simplejson.load(f)
    #     f.close()
    #     items = data.get('d')
    #     return items

if __name__ == "__main__":

    runner = Runner()
    runner.run()
    # runner.fetch()
