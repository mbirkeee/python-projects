import MySQLdb
import pyproj
import numpy
import math
import time
from password import MYSQL_PASSWORD

class Runner(object):
    """
    A collection of utilities to process the SHED10 data.  The approach taken
    here was to download the required tables into CSV files then post-process
    them, rather than to perform complicated SQL queries.  Generate lots of
    intermediate files for plotting (e.g., before aggregation, etc)
    """

    def __init__(self):

        self.users_battery = {}
        self.user_dict = {}

        self._toss_user_id = []
        self._keep_user_id = []

        self._min_time = 0
        self._max_time = 0
        self._max_time_index = 0

        self._min_time = 1481300627
        self._max_time = 1489015809

        self._aggregate_sec = 300.0

        self._gps_user_data = []

        self._max_time_index = int(float(self._max_time - self._min_time)/self._aggregate_sec)

    def filter_battery(self):
        """
        Read in all the battery records and count according to user ID.
        Compute percentage of total returned by each user, and make a
        list of those above a threshold and those below a threshold.
        """

        # Assume battery record every 5 mins for 28 days
        max_possible_battery_count = 28 * 60 * 24 / 5

        line_count = 0
        f = open("battery.csv", "r")

        for line in f:
            # print line
            line_count += 1

            line = line.strip()
            parts = line.split(",")

            user_id = parts[0]

            if user_id == 'user_id':
                print
                continue

            user_count = self.users_battery.get(user_id, 0)
            user_count += 1
            self.users_battery[user_id] = user_count

        f.close()

        print "Read %d lines" % line_count

        user_count = 1
        for user_id, value in self.users_battery.iteritems():
            percentage = 100.0 * float(value) / float(max_possible_battery_count)

            print "User %d ID: %s records: %s percent possible: %f" % \
                  (user_count, repr(user_id), repr(value), percentage)
            user_count += 1

            if percentage < 50.0:
                self._toss_user_id.append(user_id)
            else:
                self._keep_user_id.append(user_id)

        for user_id in self._toss_user_id:
            print "TOSS:", user_id

        for user_id in self._keep_user_id:
            print "KEEP", user_id

    def in_saskatoon(self, lat, lon):
        # Return False if the specified lat/lon is outside Saskatoon; else True

        if lat < 52.058367:
            return False

        if lat > 52.214608:
            return False

        if lon < -106.7649138128:
            return False

        if lon > -106.52225318:
            return False

        return True

    def filter_gps(self):
        """
        Loop through all GPS records.  Discard all that:
        - belong to users that returned less that 50% possible records
        - not within saskatoon
        - >100m accuracy
        """
        f = open("gps.csv", "r")
        f2 = open("gps_filtered_by_user.csv", "w")

        line_count = 0
        keep_count = 0
        toss_count = 0
        toss_user_count = 0

        for line in f:
            line_count += 1

            line = line.strip()
            parts = line.split(",")

            user_id = parts[0]
            lat = float(parts[2])
            lon = float(parts[3])
            accuracy = float(parts[1])
            sat_time = parts[5]

            if not user_id in self._keep_user_id:
                # print "toss < 50% user"
                toss_user_count += 1
                continue

            if not self.in_saskatoon(lat, lon):
                toss_count += 1
                continue

            if accuracy > 100.0:
                print "bad accuracy", accuracy
                toss_count += 1
                continue

            keep_count += 1

          #   if line_count > 1000000:
          #       break
            t = time.strptime(sat_time.strip(), "%a %b %d %H:%M:%S %Z %Y")
            sat_sec = int(time.mktime(t))

            line = "%s, %f, %f, %d\n" % (user_id, lat, lon, sat_sec)
            f2.write(line)

        f.close()
        f2.close()

        print "toss_count", toss_count
        print "keep_count", keep_count
        print "toss_user_count", toss_user_count

    def convert_to_utm(self):
        """
        Convert the lat/lon position to UTM and discard any points outside Saskatoon
        """
        line_count = 0
        skip_count = 0
        index = 0

        f = open("gps_filtered_no_duplicates.csv", "r")
        f2 = open("gps_utm.csv", "w")

        #f2.write("user_id, lat, long, utm_x, utm_y, time\n")
        f2.write("user_id, utm_x, utm_y, time\n")

        myProj = pyproj.Proj("+init=EPSG:32613")

        for line in f:
            line = line.strip()
            parts = line.split(",")

            user_id = parts[0].strip()
            lat = float(parts[1].strip())
            lon = float(parts[2].strip())
            sat_sec = int(parts[3].strip())

            if not self.in_saskatoon(lat, lon):
                print "Ignoring point outside saskatoon:", lat, lon
                skip_count += 1
                continue

            line_count += 1
            #if line_count > 100: break

            x, y  = myProj(lon, lat)
            #line = "%s, %f, %f, %f, %f, %d\n" % (user_id, lat, lon, x, y, sat_sec)
            line = "%s, %f, %f, %d\n" % (user_id, x, y, sat_sec)

            f2.write(line)
        f2.close()
        f.close()

    def test_sorted(self, file_name):
        """
        Ensure the CSV data is grouped by user_id and sorted by time.
        Raise an Exception if not.
        """
        user_dict = {}
        prev_user = 0
        line_count = 0

        f = open(file_name, "r")

        for line in f:

            line_count += 1
            if line_count == 1:
                continue

            parts = line.split(",")
            user_id = parts[0].strip()
            x = float(parts[1].strip())
            y = float(parts[2].strip())
            sat_sec = int(parts[3].strip())

            if user_id != prev_user:
                prev_user = user_id

                if user_dict.has_key(user_id):
                    raise ValueError("ERROR! %s: users not grouped! line: %s" %
                                     (file_name, line_count))
                else:
                    print "New User", user_id
                    user_dict[user_id] = {'p':sat_sec, 'c' : 1}
            else:
                user_data = user_dict.get(user_id)

                if sat_sec <= user_data.get('p'):
                    raise ValueError("ERROR! %s: points not sorted! line: %s" %
                                     (file_name, line_count))

                user_data['p'] = sat_sec
                count = user_data.get('c')
                user_data['c'] = count + 1

        f.close()

        total_records = 0
        for user_id, user_data in user_dict.iteritems():
            print "user_id: %s records: %d" % (user_id, user_data.get('c'))
            total_records += user_data.get('c')

        print "%s: Total records: %d" %(file_name, total_records)


    def process_bin(self, bin, fp, user_id):
        """
        Compute the average time, x position, y position, and write to file
        """
        if len(bin) == 0:
            return

        # print bin

        x_total = 0
        y_total = 0
        t_total = 0

        for item in bin:
            t_total += item[0]
            x_total += item[1]
            y_total += item[2]

        item_count = float(len(bin))

        bin_time = int(t_total/item_count)
        x_ave = x_total / item_count
        y_ave = y_total / item_count

        fp.write("%s, %f, %f, %d\n" % (user_id, x_ave, y_ave, bin_time))

    def min_max_time(self):

        input_file = "gps_utm.csv"

        self.test_sorted(input_file)

        min_time = None
        max_time = None

        line_count = 0
        f = open(input_file, "r")
        for line in f:

            line_count += 1
            if line_count == 1:
                continue

            parts = line.split(",")
            user_id = parts[0].strip()
            x = float(parts[1].strip())
            y = float(parts[2].strip())
            sat_sec = int(parts[3].strip())

            if min_time is None: min_time = sat_sec
            if max_time is None: max_time = sat_sec

            if sat_sec < min_time:
                min_time = sat_sec

            if sat_sec > max_time:
                max_time = sat_sec

        f.close()
        print "min_time: %d" % min_time
        print "max_time: %d" % max_time

        interval = max_time - min_time
        print "interval: %d" % interval
        periods = int(float(interval)/float(self._aggregate_sec))
        print "periods: %d" % periods

        return min_time, max_time

    def process_trip(self, trip_points):

        total_distance = 0
        total_time = len(trip_points) - 1

        for i in xrange(len(trip_points)-1):
            item_1 = trip_points[i]
            item_2 = trip_points[i+1]
            x_start = item_1[0]
            y_start = item_1[1]
            x_end = item_2[0]
            y_end = item_2[1]

            distance = math.sqrt(math.pow((x_end-x_start),2) + math.pow((y_end-y_start),2))

            total_distance += distance

        start_item = trip_points[0]
        end_item = trip_points[-1]

        print start_item
        print end_item

        start_time = start_item[2]
        end_time = end_item[2]

        start_time = start_time * self._aggregate_sec + self._min_time
        end_time = (end_time + 1) * self._aggregate_sec + self._min_time
        print start_time
        print end_time

        print "TRIP DIST: %f TIME: %d %d %d" % (total_distance, total_time, start_time, end_time)
        return total_distance, total_time, start_time, end_time


    def make_one_trip_csv(self, user_id, trip_count, start_sec, stop_sec):
        print "make trip csv", user_id, trip_count, start_sec, stop_sec

        file_name = "user_trips/user_trip_%d_%d.csv" % (user_id, trip_count)

        f = open(file_name, "w")
        f.write("x_utm, y_utm, sec\n")
        # f.close()

        object_id = 0
        for item in self._gps_user_data:
            user_id = item[0]
            x_utm = item[1]
            y_utm = item[2]
            sat_sec = item[3]

            #print sat_sec, start_sec, stop_sec
            if sat_sec < start_sec or sat_sec > stop_sec:
                continue

            f.write("%f,%f,%d\n" % (x_utm, y_utm, sat_sec))
            # print user_id, x_utm, y_utm, sat_sec
            object_id += 1

        f.close()

    def make_trip_csvs(self, user_id=None, n=0):

        user_id_in = user_id

        f = open("gps_utm.csv", "r")

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")

            user_id = int(parts[0].strip())
            if user_id == user_id_in:
                x_utm = float(parts[1].strip())
                y_utm = float(parts[2].strip())
                sat_sec = int(parts[3].strip())

                self._gps_user_data.append((user_id, x_utm, y_utm, sat_sec))

        f.close()

        trip_data_filename = "trip_data_%d.csv" % n

        f = open(trip_data_filename, "r")
        line_count=0
        trip_count = 0

        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            #print parts

            user_id = int(parts[0].strip())
            start_sec = int(parts[3].strip())
            stop_sec = int(parts[4].strip())

            if user_id == user_id_in:

                trip_length = stop_sec - start_sec
                if trip_length >  15 * 60:
                    trip_count += 1
                    self.make_one_trip_csv(user_id, trip_count, start_sec, stop_sec)
                else:
                    print "skipping trip length", trip_length
        f.close()

    def detect_trips(self, n=1):

        size = 100

        myProj = pyproj.Proj("+init=EPSG:32613")

        start_x, start_y  = myProj(-106.7649138128, 52.058367)
        stop_x, stop_y = myProj(-106.52225318, 52.214608 )

        x_bins = 1 + int((stop_x - start_x) / float(size))
        y_bins = 1 + int((stop_y - start_y) / float(size))

        input_file = "aggregated_2.csv"
        output_file = "trip_data_%d.csv" % n

        f = open(input_file, "r")
        f2 = open(output_file, "w")
        f2.write("user_id,dist,duration,start_time,stop_time\n")

        line_count = 0

        index_in_trip = {}
        line_list = []

        prev_user_id = None
        prev_index = 0
        prev_time = 0
        prev_x = None
        prev_y = None

        trip_points = []

        for line in f:

            line_count += 1
            if line_count == 1:
                continue

            parts = line.split(",")
            user_id = parts[0].strip()
            x = int(parts[1].strip())
            y = int(parts[2].strip())
            time = int(parts[3].strip())
            points = int(parts[4].strip())
            index = int(parts[5].strip())

            if x == -1: continue

            # Line list is used to compute the heatmaps
            line_list.append((x,y,points,index))
            # print user_id, x, y, time, points

            if user_id != prev_user_id:
                if len(trip_points) > 0:
                    print "throw away trip info when user_id changes"
                    trip_points = []

            # At this point we must have the same user ID
            elif len(trip_points) > 0:
                # We are in a trip
                trip_points.append((x,y,time,index))

                if self.trip_done(trip_points, n):
                    trimmed = trip_points[:-n]

                    for item in trimmed:
                        # print item
                        index = item[3]
                        # print index
                        index_in_trip[index] = True

                    # Make a CSV file for this individual trip
                    # if len(trimmed) > 10:
                    #     self.trip_csv(trimmed)
                    distance, duration, start_time, end_time = self.process_trip(trimmed)

                    f2.write("%s,%f,%d, %d, %d\n" % (user_id, distance, duration, start_time, end_time))
                    trip_points = []
            else:
                # We are not in a trip
                if x != prev_x or y != prev_y:
                    print "Detected trip start!!"
                    trip_points = [(prev_x, prev_y, prev_time, prev_index), (x, y, time, index)]
                    # print trip_points
                    # raise ValueError("test 1")
                else:
                    # Not in trip plus not a trip start
                    pass

            prev_user_id = user_id
            prev_index = index
            prev_time = time
            prev_x = x
            prev_y = y

        f2.close()
        f.close()

        # return

        heatmap_trip_yes = numpy.zeros((x_bins, y_bins), dtype=numpy.uint32)
        heatmap_trip_no = numpy.zeros((x_bins, y_bins), dtype=numpy.uint32)

        count_trip_yes = 0
        count_trip_no = 0
        count_trip_ignored = 0

        for line in line_list:
            x = line[0]
            y = line[1]
            points = line[2]
            index = line[3]

            if x >= x_bins:
                print "ERROR", x, x_bins
                continue

            if y >= y_bins:
                print "ERROR", y, y_bins
                continue

            # print line
            if index_in_trip.has_key(index):
                count_trip_yes += 1
                # print "point in a trip"
                heatmap_trip_yes[x,y] += 1
            elif points > 0:
                # print "point not in trip"
                count_trip_no += 1
                heatmap_trip_no[x,y] += 1
            else:
                #print "point ignored"
                count_trip_ignored += 1

        print "count_trip_yes", count_trip_yes
        print "count_trip_no", count_trip_no
        print "count_trip_ignored", count_trip_ignored

        # Write the heatmap to a CSV file
        f = open("heatmap_trip_yes_%d.csv" % n, "w")
        f.write("utm_center_x, utm_center_y, count\n")

        f2 = open("heatmap_trip_no_%d.csv" % n, "w")
        f2.write("utm_center_x, utm_center_y, count\n")

        for x in xrange(x_bins):
            # Compute the UTM bin center in X direction
            x_utm = start_x + x * size + int(size/2)
            for y in xrange(y_bins):
                # Compute the UTM bin center in Y direction
                y_utm = start_y + y * size + int(size/2)

                count = heatmap_trip_yes[x,y]
                if count > 0:
                    # Only write out bins with 1 or more visits
                    f.write("%f,%f,%d\n" % (x_utm, y_utm, count))

                count = heatmap_trip_no[x,y]
                if count > 0:
                    # Only write out bins with 1 or more visits
                    f2.write("%f,%f,%d\n" % (x_utm, y_utm, count))

        f.close()
        f2.close()


        print "min_time", self._min_time
        print "max_time", self._max_time

    def trip_stats_length(self, n):

        f = open("trip_data_%d.csv" % n)

        result = {}

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(',')
            length = int(float(parts[1].strip()))

            count = result.get(length, 0)
            count +=1

            result[length] = count

        return result

    def trip_length_plot(self):
        result1 = self.trip_stats_length(1)
        result3 = self.trip_stats_length(3)
        result5 = self.trip_stats_length(5)

        min_length = None
        max_length = None

        for length, count in result1.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_length is None or length < min_length:
                min_length = length

            if max_length is None or length > max_length:
                max_length = length

        for length, count in result3.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_length is None or length < min_length:
                min_length = length

            if max_length is None or length > max_length:
                max_length = length

        for length, count in result5.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_length is None or length < min_length:
                min_length = length

            if max_length is None or length > max_length:
                max_length = length

        f = open("plot_trip_length.csv", "w")
        f.write("cells,1,3,5\n")

        for i in xrange(max_length + 5):

            count_1 = 0
            for length, count in result1.iteritems():
                if length >= i+1:
                    count_1 += count

            count_3 = 0
            for length, count in result3.iteritems():
                if length >= i+1:
                    count_3 += count

            count_5 = 0
            for length, count in result5.iteritems():
                if length >= i+1:
                    count_5 += count

            print i+1,count_1, count_3, count_5
            f.write("%d,%d,%d,%d\n" % (i+1, count_1, count_3, count_5))

        f.close()

    def trip_stats_time(self, n):

        f = open("trip_data_%d.csv" % n)

        result = {}

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(',')
            t = int(float(parts[2].strip()))

            count = result.get(t, 0)
            count +=1

            result[t] = count

        return result

    def trip_time_plot(self):
        result1 = self.trip_stats_time(1)
        result3 = self.trip_stats_time(3)
        result5 = self.trip_stats_time(5)

        min_time = None
        max_time = None

        for t, count in result1.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_time is None or t < min_time:
                min_time = t

            if max_time is None or t > max_time:
                max_time = t

        for t, count in result3.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_time is None or t < min_time:
                min_time = t

            if max_time is None or t > max_time:
                max_time = t

        for t, count in result5.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_time is None or t < min_time:
                min_time = t

            if max_time is None or t > max_time:
                max_time = t

        f = open("plot_trip_time.csv", "w")
        f.write("cells,1,3,5\n")

        for i in xrange(max_time + 5):

            count_1 = 0
            for t, count in result1.iteritems():
                if t >= i+1:
                    count_1 += count

            count_3 = 0
            for t, count in result3.iteritems():
                if t >= i+1:
                   count_3 += count

            count_5 = 0
            for t, count in result5.iteritems():
                if t >= i+1:
                    count_5 += count

            print i+1,count_1, count_3, count_5
            f.write("%d,%d,%d,%d\n" % (i+1, count_1, count_3, count_5))

        f.close()


    def trip_stats_trip_count(self, n):

        f = open("trip_data_%d.csv" % n)

        result = {}

        line_count = 0
        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(',')
            user_id = parts[0].strip()

            count = result.get(user_id, 0)
            count +=1

            result[user_id] = count

        return result

    def trip_stats(self):

        result1 = self.trip_stats_trip_count(1)
        result3 = self.trip_stats_trip_count(3)
        result5 = self.trip_stats_trip_count(5)

        min_count = None
        max_count = None

        for user_id, count in result1.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_count is None or count < min_count:
                min_count = count

            if max_count is None or count > max_count:
                max_count = count

        for user_id, count in result3.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_count is None or count < min_count:
                min_count = count

            if max_count is None or count > max_count:
                max_count = count

        for user_id, count in result5.iteritems():
            #print "n: %d, user_id: %s trips: %d" % (n, user_id, count)

            if min_count is None or count < min_count:
                min_count = count

            if max_count is None or count > max_count:
                max_count = count

        print min_count, max_count

        f = open("plot_trip_counts.csv", "w")
        f.write("trips,1,3,5\n")

        for i in xrange((max_count - min_count) + 10):
            tc = i + min_count - 5
            #print tc

            user_count_1 = 0
            for user_id, count in result1.iteritems():
                if count > tc:
                    user_count_1 += 1

            user_count_3 = 0
            for user_id, count in result3.iteritems():
                if count > tc:
                    user_count_3 += 1

            user_count_5 = 0
            for user_id, count in result5.iteritems():
                if count > tc:
                    user_count_5 += 1

            print tc,user_count_1,user_count_3,user_count_5
            f.write("%d,%d,%d,%d\n" % (tc,user_count_1, user_count_3, user_count_5))

        f.close()

    def trip_csv(self, trip):

        myProj = pyproj.Proj("+init=EPSG:32613")

        size = 100
        start_x, start_y  = myProj(-106.7649138128, 52.058367)
        stop_x, stop_y = myProj(-106.52225318, 52.214608 )

        f = open("trip.csv", "w")
        f.write("x_start,y_start, x_end, y_end\n")

        for i in xrange(len(trip)-1):
            item = trip[i]
            item2 = trip[i+1]
            x = item[0]
            y = item[1]

            x2 = item2[0]
            y2 = item2[1]

            x_utm = start_x + x * size + int(size/2)
            y_utm = start_y + y * size + int(size/2)

            x2_utm = start_x + x2 * size + int(size/2)
            y2_utm = start_y + y2 * size + int(size/2)

            print x,y,x_utm, y_utm
            f.write("%f,%f,%f,%f\n" % (x_utm, y_utm, x2_utm, y2_utm))

        f.close()

    def trip_done(self, trip_points, n):

        # print "***************************"
        # for item in trip_points:
        #     print item
        #
        # print "---------------------------"
        if len(trip_points) < n + 1:
            return False

        in_trip = False

        for i in xrange(n):
            item1 = trip_points[-(i+1)]
            item2 = trip_points[-(i+2)]

            # print "compare", item1, item2

            x1 = item1[0]
            y1 = item1[1]

            x2 = item2[0]
            y2 = item2[1]

            if x1 != x2:
                in_trip = True
                break

            if y1 != y2:
                in_trip = True
                break


        # print "###########################"

        if in_trip:
            return False

        return True


    def aggregate_2(self, size=100):
        """
        Loop over all the GPS datapoints.  Determine which time bin index they fall into.
        """


        # THE DATA MUST BE GROUPED BY USER AND SORTED BY TIME!!!!!
        input_file = "gps_utm.csv"
        output_file = "aggregated_2.csv"

        myProj = pyproj.Proj("+init=EPSG:32613")

        start_x, start_y = myProj(-106.7649138128, 52.058367)
        stop_x, stop_y = myProj(-106.52225318, 52.214608)

        # x_bins = 1 + int((stop_x - start_x) / float(size))
        # y_bins = 1 + int((stop_y - start_y) / float(size))

        data = {}
        f = open(input_file, "r")
        line_count = 0

        for line in f:

            line_count += 1
            if line_count == 1:
                continue

            parts = line.split(",")

            user_id = parts[0].strip()
            x = float(parts[1].strip())
            y = float(parts[2].strip())
            sat_sec = int(parts[3].strip())

            time_offset = sat_sec - self._min_time
            time_index = int(float(time_offset)/self._aggregate_sec)

            # print "time bin index: %d" % time_bin_index

            user_data = data.get(user_id, {})
            time_bin_data = user_data.get(time_index, [])
            time_bin_data.append((x, y))
            user_data[time_index] = time_bin_data
            data[user_id] = user_data

            # if line_count > 100000: break

        f.close()

        f2 = open(output_file, "w")
        f2.write("user_id,x,y,time,points\n")

        out_index = 0
        for user_id, user_data in data.iteritems():
            print "processing user_id", user_id
            result = self.aggregate_user_trip(user_data, start_x, start_y, size)

            for item in result:
                # print item
                f2.write("%s,%d,%d,%d,%d,%d\n" % (user_id, item[0], item[1], item[2], item[3], out_index))
                out_index += 1

        f2.close()

    def aggregate_user_trip(self, user_data, start_x, start_y, size):

        prev_x = -1
        prev_y = -1

        result = []

        for i in xrange(self._max_time_index + 1):
            points = user_data.get(i)

            if points is None:
                # Use the previous position
                result.append((prev_x, prev_y, i, 0))
                continue

            ave_x = 0
            ave_y = 0
            for item in points:
                ave_x += item[0]
                ave_y += item[1]

            x = ave_x / float(len(points))
            y = ave_y / float(len(points))

            # Compute the bin index of the average location
            x_index = int((x - float(start_x))/float(size))
            y_index = int((y - float(start_y))/float(size))

            result.append((x_index, y_index, i, len(points)))

            prev_x = x_index
            prev_y = y_index

        return result


    def aggregate(self):
        """
        Aggregate the data into bins of duration aggregate_sec
        """

        # THE DATA MUST BE GROUPED BY USER AND SORTED BY TIME!!!!!
        input_file = "gps_utm.csv"
        output_file = "aggregated.csv"

        # Ensure input data is grouped by user ID and sorted by time
        self.test_sorted(input_file)

        aggregate_sec = 60

        f = open(input_file, "r")
        f2 = open(output_file, "w")

        f2.write("user_id, utm_x, utm_y, time_sec\n")

        user_id = 0
        line_count = 0
        prev_user_id = 0
        bin_stop_time = 0

        bin = []
        for line in f:

            line_count += 1
            if line_count == 1:
                continue

            parts = line.split(",")
            user_id = parts[0].strip()
            x = float(parts[1].strip())
            y = float(parts[2].strip())
            sat_sec = int(parts[3].strip())

            if user_id != prev_user_id:
                # New user - process previous user's last bin
                self.process_bin(bin, f2, prev_user_id)
                prev_user_id = user_id

                # New user - start a new bin
                bin_start_time = sat_sec
                bin_stop_time = bin_start_time + aggregate_sec
                bin = [(sat_sec, x, y)]

            elif sat_sec >= bin_stop_time:
                # Have exceeded current bin's end time
                self.process_bin(bin, f2, user_id)

                # Start a new bin
                bin_start_time = sat_sec
                bin_stop_time = bin_start_time + aggregate_sec
                bin = [(sat_sec, x, y)]

            else:
                # Same user and point within current bin
                bin.append((sat_sec, x, y))

        # Process any remainng bin when end of file reached
        self.process_bin(bin, f2, user_id)

        f.close()
        f2.close()

        self.test_sorted(output_file)

    def remove_duplicates(self):
        """
        Remove any duplicate records.  Write results to file:
        - GROUPED BY USER ID
        - SORTED BY TIME
        """
        f = open("gps_filtered_by_user.csv")

        data = {}
        dup_count = 0
        err_count = 0
        line_count = 0

        for line in f:
            parts = line.split(",")
            user_id = parts[0].strip()
            lat = parts[1].strip()
            lon = parts[2].strip()
            sat_sec = int(parts[3].strip())

            user_data = data.get(user_id, {})
            gps_data = user_data.get(sat_sec, {})

            have_lat = gps_data.get('1', None)
            have_lon = gps_data.get('2', None)

            if have_lat is None and have_lon is None:
                gps_data = {'1': lat, '2': lon}
                user_data[sat_sec] = gps_data
                data[user_id] = user_data

            elif lat == have_lat and lon == have_lon:
                # print "duplicate point detected"
                dup_count += 1
            else:
                err_count += 1
                #print "-------------------------"
                #print "ERROR!!! two positions same time!!!!", user_id, sat_sec, lat, lon
                #print "ERROR!!! two positions same time!!!!", user_id, sat_sec, have_lat, have_lon

            line_count += 1
            # if line_count > 1000: break

        f.close()

        print "duplicate count", dup_count
        print "error count", err_count

        f2 = open("gps_filtered_no_duplicates.csv", "w")

        for user_id, user_data in data.iteritems():

            points =[]
            for sat_sec, pos in user_data.iteritems():
                points.append((sat_sec, pos))

            points = sorted(points)

            for item in points:
                pos = item[1]
                sat_sec = item[0]
                line = "%s, %s, %s, %d\n" % (user_id, pos.get('1'), pos.get('2'), sat_sec)
                f2.write(line)

        f2.close()

    def process_dwell_time(self, dwell_time_list, dwt, dwc, x, y):
        if len(dwell_time_list) < 2:
            return

        start_time = min(dwell_time_list)
        stop_time = max(dwell_time_list)
        #print "dwell", start_time, stop_time, stop_time-start_time

        dwell_time_sec =  stop_time - start_time

        dwt[x, y] += stop_time - start_time
        dwc[x, y] += 1

    def bin_aggregated(self, size=1600, user=None):

        user_name = "all" if user is None else "%s" % user

        myProj = pyproj.Proj("+init=EPSG:32613")

        start_x, start_y  = myProj(-106.7649138128, 52.058367)
        stop_x, stop_y = myProj(-106.52225318, 52.214608 )

        x_bins = 1 + int((stop_x - start_x) / float(size))
        y_bins = 1 + int((stop_y - start_y) / float(size))

        print "size (m):", size, "X bins:", x_bins, "Y bins:", y_bins

        f = open("aggregated.csv", "r")
        line_count = 0
        consider_count = 0

        prev_user_id = 0
        prev_index_x = 0
        prev_index_y = 0

        dwell_time = []

        heatmap = numpy.zeros((x_bins, y_bins), dtype=numpy.uint32)
        dwt = numpy.zeros((x_bins, y_bins), dtype=numpy.uint32)
        dwc = numpy.zeros((x_bins, y_bins), dtype=numpy.uint32)

        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            user_id = int(parts[0].strip())
            x = float(parts[1].strip())
            y = float(parts[2].strip())
            t = int(parts[3].strip())

            # Only process specified user_id_in
            if user is not None and user_id != user: continue

            # Compute the bin index of the location
            x_index = int((x - float(start_x))/float(size))
            y_index = int((y - float(start_y))/float(size))

            # print x, y, x_index, y_index

            if y_index < 0 or y_index >= y_bins:
                # print "ignoring y_index outside target area", y_index
                continue

            if x_index < 0 or x_index >= x_bins:
                # print "ignoring x_index outside target area", x_index
                continue

            consider_count += 1

            if user_id != prev_user_id:
                # This counts as a new visit
                self.process_dwell_time(dwell_time, dwt, dwc, x_index, y_index)
                prev_user_id = user_id
                heatmap[x_index, y_index] += 1
                dwell_time=[t]

            elif y_index != prev_index_y:
                # Transitioned to new bin in Y direction
                self.process_dwell_time(dwell_time, dwt, dwc, x_index, y_index)

                prev_index_y = y_index
                heatmap[x_index, y_index] += 1
                dwell_time=[t]

            elif x_index !=  prev_index_x:
                # Transitioned to new bin in X direction
                self.process_dwell_time(dwell_time, dwt, dwc, x_index, y_index)
                prev_index_x = x_index
                heatmap[x_index, y_index] += 1
                dwell_time=[t]
            else:
                # same user same bin... NOT a new visit
                dwell_time.append(t)

            # if line_count > 100: break

        # Process any remaining bin at end of file
        self.process_dwell_time(dwell_time, dwt, dwc, x_index, y_index)
        f.close()

        # Write the heatmap to a CSV file
        f = open("visit_heatmap_%s_%d.csv" % (user_name, size), "w")
        f.write("utm_center_x, utm_center_y, visits\n")

        f2 = open("dwell_heatmap_%s_%d.csv" % (user_name, size), "w")
        f2.write("utm_center_x, utm_center_y, dwell_time\n")

        # Dict to make plot of visit frequency
        visit_dict = {}
        dwell_dict = {}

        for x in xrange(x_bins):
            # Compute the UTM bin center in X direction
            x_utm = start_x + x * size + int(size/2)
            for y in xrange(y_bins):
                # Compute the UTM bin center in Y direction
                y_utm = start_y + y * size + int(size/2)
                visits = heatmap[x,y]
                if visits > 0:
                    # Only write out bins with 1 or more visits
                    f.write("%f, %f, %d\n" % (x_utm, y_utm, visits))

                    count = visit_dict.get(visits, 0)
                    count += 1
                    visit_dict[visits] = count

                dt = dwt[x,y]
                dc = dwc[x,y]

                if dt != 0:
                    #print "dwell time", dt, dc
                    ave_dwell_time = int(float(dt)/float(dc))
                    f2.write("%f, %f, %d\n" % (x_utm, y_utm, ave_dwell_time))

                    ave_dwell_15 = 1 + int(float(ave_dwell_time)/float(15*60))

                    count = dwell_dict.get(ave_dwell_15, 0)
                    count += 1
                    dwell_dict[ave_dwell_15] = count
        f.close()
        f2.close()

        bin_list = []
        for visits, bins in visit_dict.iteritems():
            #print visits, bins
            bin_list.append((visits, bins))

        # Sort by visit count for plotting
        bin_list = sorted(bin_list)

        # Write out to CSV file
        f = open("visit_plot_%s_%d.csv" % (user_name, size), "w")
        for item in bin_list:
            f.write("%d, %d\n" % (item[0], item[1]))

        f.close()

        dwell_list = []
        for dwell, bins in dwell_dict.iteritems():
            dwell_list.append((dwell, bins))

        dwell_list = sorted(dwell_list)

        f = open("dwell_plot_%s_%d.csv" % (user_name, size), "w")
        for item in dwell_list:
            f.write("%d, %d\n" % (15*item[0], item[1]))

        f.close()

    def make_visit_csv(self, user=None):

        data = {}

        user_name = "all" if user is None else "%s" % user

        files = [
            "visit_plot_%s_100.csv" % user_name,
            "visit_plot_%s_400.csv" % user_name,
            "visit_plot_%s_1600.csv" % user_name,
        ]

        for i, file_name in enumerate(files):

            f = open(file_name, "r")
            for line in f:
                parts = line.split(",")
                visits = int(parts[0].strip())
                bins = int(parts[1].strip())

                x = data.get(visits, {})
                x[i] = bins
                data[visits] = x
            f.close()

        lst = []
        for visits, x in data.iteritems():
            # print visits, x
            lst.append((visits, x))

        lst = sorted(lst)

        f = open("visit_%s.csv" % user_name, "w")
        for item in lst:
            print item[0], item[1]
            x = item[1]
            f.write("%d, %f, %f, %f\n" % (item[0], x.get(0,0.9), x.get(1,0.9), x.get(2,0.9)))

        f.close()

    def make_dwell_csv(self, user=None):

        data = {}

        user_name = "all" if user is None else "%s" % user

        files = [
            "dwell_plot_%s_100.csv" % user_name,
            "dwell_plot_%s_400.csv" % user_name,
            "dwell_plot_%s_1600.csv" % user_name,
        ]

        for i, file_name in enumerate(files):

            f = open(file_name, "r")
            for line in f:
                parts = line.split(",")
                dwell = int(parts[0].strip())
                bins = int(parts[1].strip())

                x = data.get(dwell, {})
                x[i] = bins
                data[dwell] = x
            f.close()

        lst = []
        for dwell, x in data.iteritems():
            # print visits, x
            lst.append((dwell, x))

        lst = sorted(lst)

        f = open("dwell_%s.csv" % user_name, "w")
        for item in lst:
            print item[0], item[1]
            x = item[1]
            f.write("%d, %f, %f, %f\n" % (item[0], x.get(0,0.9), x.get(1,0.9), x.get(2,0.9)))

        f.close()

class MySQL(object):
    """
    Get MYSQL table contents and write into CSV file for local processing
    """
    def get_gps(self):

        db = MySQLdb.connect(host="crepe.usask.ca", user="slb405",
            db="SHED9", passwd="%s" % MYSQL_PASSWORD)

        c = db.cursor()

        sql = "select user_id, accu, lat, lon, provider, satellite_time, record_time from gps"

        c.execute(sql)

        f = open("gps_shed9.csv", "w")

        row_count = 0
        while True:
            row = c.fetchone()
            if row is None: break
            f.write("%s, %s, %s, %s, %s, %s, %s\n" % \
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            row_count += 1

        f.close()

    def get_battery(self):

        db = MySQLdb.connect(host="crepe.usask.ca", user="slb405", db="SHED9", passwd="abgEFIJXl_%Q18")

        c = db.cursor()

        # sql = "select user_id, accu, lat, lon, provider, satellite_time from gps where user_id=1361"
        sql = "select user_id, record_time from battery"

        c.execute(sql)

        f = open("battery_shed9.csv", "w")

        row_count = 0
        while True:
            row = c.fetchone()
            if row is None: break

            f.write("%s, %s\n" % (row[0], row[1]))
            row_count += 1

        f.close()

if __name__ == "__main__":

    mysql = MySQL()
    mysql.get_battery()
    mysql.get_gps()

    raise ValueError("done")

    runner = Runner()

#    runner.filter_battery()
#    runner.filter_gps()
#    runner.remove_diplicates()
    runner.convert_to_utm()
#    runner.aggregate()
#    runner.min_max_time()

#    runner.aggregate_2()
#    runner.detect_trips(n=2)

#    runner.trip_stats()
#    runner.trip_length_plot()
#    runner.trip_time_plot()

#    runner.make_trip_csvs(user_id=1323, n=2)
#    runner.make_trip_csvs(user_id=559, n=2)
#    runner.make_trip_csvs(user_id=1301, n=2)
#    runner.make_trip_csvs(user_id=1302, n=2)

#    runner.bin_aggregated(user=user, size=100)
#    runner.bin_aggregated(user=user, size=400)
#    runner.bin_aggregated(user=user, size=1600)
#    runner.make_visit_csv(user=user)
#    runner.make_dwell_csv(user=user)



