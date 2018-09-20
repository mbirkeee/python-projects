# This file contains code to fetch data from the open data portal.  The
# data must come in batches of 1000.  The data is saved as json, then
# post-processed into single CSV files

import time
import simplejson
import os
import scandir
import urllib2

class Runner(object):

    def __init__(self):

        self._base = "http://opendata-saskatoon.cloudapp.net:8080/v1/SaskatoonOpenDataCatalogueBeta"
        self._json_path = "data/open_data/2018_08_05/json"
        self._csv_path = "data/open_data/2018_08_05/csv"

    def fetch(self, table):

        # This seems to work to get data for just one stop
        #    url = "TransitStopTimes?$filter=%s&format=json" % urllib.quote("stop_id eq '3094'")
        #
        # Get stops from 3000 to 4000
        #    url = "TransitStops?$filter=%s&format=json" % urllib.quote("stop_id ge '3000' and stop_id lt '4000'")


        next_partition_key = None
        next_row_key = None
        index = 0

        while True:

            if next_partition_key is None:
                url = "%s/%s?format=json" % (self._base, table)
            else:
                url = "%s/%s?NextPartitionKey=%s&NextRowKey=%s&format=json" % \
                      (self._base, table, next_partition_key, next_row_key)

            print url

            response = urllib2.urlopen(url)
            json = response.read()
            response.close()

            d = simplejson.loads(json)

            stuff = d.get('d')

            # See if we should continue
            info = response.info()
            next_partition_key = info.get('x-ms-continuation-NextPartitionKey')
            next_row_key = info.get('x-ms-continuation-NextRowKey')

            print "Read:", len(stuff), "next_partition", next_partition_key
            # print "next_row", next_row_key

            f = open("%s/%s/file_%d.json" % (self._json_path, table, index), "w")
            f.write(json)
            f.close()

            index += 1
            if next_partition_key is None:
                break

            time.sleep(1)

        print "Done"

    def get_json_files(self, table):
        result = []
        path = os.path.join(self._json_path, table)
        for item in scandir.scandir(path):

            if not item.is_file():
                print "skipping item"
                continue

            print item.path

            if not item.path.endswith(".json"):
                print "skipping file", item.path
                continue

            result.append(item.path)

        return result

    def get_items(self, file):

        f = open(file, "r")
        data = simplejson.load(f)
        f.close()
        items = data.get('d')
        return items

    def get_header(self, table):
        if table == 'TransitStopTimes':
            return "stop_id,trip_id,arrival_time,departure_time,stop_sequence,shape_dist_traveled"
        elif table == 'TransitTrips':
            return "trip_id,route_id,block_id,shape_id,service_id,direction,bikes,wheelchairs,headsign"
        elif table == 'TransitRoutes':
            return "route_id,route_type,route_color,text_color,name_short,name_long"
        elif table == 'TransitStops':
            return "stop_id,stop_code,stop_lat,stop_lon,location_type,wheelchair_boarding,name"
        elif table == 'TransitShapes':
            return "shape_id,shape_lat,shape_lon,point_seq,dist"

        raise ValueError("No header for table: %s" % table)

    def get_item_processor(self, table):
        if table == 'TransitStopTimes':
            return self.process_item_transit_stop_time
        elif table == 'TransitTrips':
            return self.process_item_transit_trips
        elif table == 'TransitRoutes':
            return self.process_item_transit_routes
        elif table == 'TransitStops':
            return self.process_item_transit_stops
        elif table == 'TransitShapes':
            return self.process_item_transit_shapes

        raise ValueError("No item processor for table: %s" % table)

    def process_item_transit_shapes(self, item):
        #print item
        shape_id = item.get('shape_id')
        shape_lat = item.get('shape_pt_lat')
        shape_lon = item.get('shape_pt_lon')
        point_seq = item.get('shape_pt_sequence')
        dist = item.get('shape_dist_traveled')

        return "%s,%s,%s,%s,%s" % (shape_id, shape_lat, shape_lon, point_seq, dist)

    def process_item_transit_stops(self, item):
        # print item
        stop_id = item.get('stop_id')
        stop_code = item.get('stop_code')
        stop_lat = item.get('stop_lat')
        stop_lon = item.get('stop_lon')
        loc_type = item.get('location_type')
        wheelchair = item.get('wheelchair_boarding')
        name = item.get('stop_name')

        if name.find(',') > 0:
            name = name.replace(",", "")
            print "removed comma from name", name

        return "%s,%s,%s,%s,%s,%s,%s" % (stop_id, stop_code, stop_lat, stop_lon, loc_type, wheelchair, name)

    def process_item_transit_routes(self, item):
        # print item
        route_id = item.get('route_id')
        route_type = item.get('route_type')
        name_long = item.get('route_long_name')
        name_short = item.get('route_short_name')
        route_color = item.get('route_color')
        text_color = item.get('route_text_color')

        if name_long.find(',') > 0:
            name_long = name_long.replace(",", "")
            print "removed comma from name", name_long

        return "%s,%s,%s,%s,%s,%s" % (route_id, route_type, route_color, text_color, name_short, name_long)

    def process_item_transit_trips(self, item):
        print item
        trip_id = item.get('trip_id')
        route_id = item.get('route_id')
        block_id = item.get('block_id')
        shape_id = item.get('shape_id')
        service_id = item.get('service_id')
        direction = item.get('direction_id')
        bikes = item.get('bikes_allowed')
        wheelchairs = item.get('wheelchair_accessible')
        headsign = item.get('trip_headsign')

        return "%s,%s,%s,%s,%s,%s,%s,%s,%s" % \
               (trip_id, route_id, block_id, shape_id, service_id, direction, bikes, wheelchairs, headsign)

    def process_item_transit_stop_time(self, item):
        # print item
        stop_id = item.get('stop_id')
        trip_id = item.get('trip_id')
        arrival_time = item.get('arrival_time')
        departure_time = item.get('departure_time')
        stop_sequence = item.get('stop_sequence')
        dist_travelled = item.get('shape_dist_traveled')
        return "%s,%s,%s,%s,%s,%s" % (stop_id, trip_id, arrival_time, departure_time, stop_sequence, dist_travelled)

    def process(self, table):

        # First, must open an output file
        csv_file = os.path.join("%s/my-%s.csv" % (self._csv_path, table))

        if os.path.exists(csv_file):
            os.remove(csv_file)

        f = open(csv_file, "w")

        header = self.get_header(table)
        f.write("%s\n" % header)
        item_processor = self.get_item_processor(table)

        file_list = self.get_json_files(table)
        for file in file_list:
            print "processing file:", file

            items = self.get_items(file)
            for item in items:
                csv = item_processor(item)
                f.write("%s\n" % csv)

        f.close()

if __name__ == "__main__":

    runner = Runner()
#    runner.fetch("TransitStopTimes")
#    runner.fetch("TransitTrips")
    runner.fetch("TransitStops")
    runner.fetch("TransitRoutes")
    runner.fetch("TransitShapes")
#    runner.fetch("TransitCalendar")

#    runner.process("TransitStopTimes")
#    runner.process("TransitTrips")
    runner.process('TransitStops')
    runner.process('TransitRoutes')
    runner.process('TransitShapes')
