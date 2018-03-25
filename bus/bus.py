import pyproj
import numpy
import math
import time
import simplejson
import os
import scandir


TOP = """
<!DOCTYPE html>
<html>
  <head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
    <meta charset="utf-8">
    <title>Simple Polylines</title>
    <style>
      /* Always set the map height explicitly to define the size of the div
       * element that contains the map. */
      #map {
        height: 100%;
      }
      /* Optional: Makes the sample page fill the window. */
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script>

      // This example creates a 2-pixel-wide red polyline showing the path of
      // the first trans-Pacific flight between Oakland, CA, and Brisbane,
      // Australia which was made by Charles Kingsford Smith.

      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 12,
          center: {lat: 52.2, lng: -106.65},
          mapTypeId: 'terrain'
        });

        var flightPlanCoordinates = [
"""

MIDDLE = """
        ];
        var flightPath = new google.maps.Polyline({
          path: flightPlanCoordinates,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath.setMap(map);
        var trip = {
"""


BOTTOM = """
        };


        for (var point in trip) {
          var circle = new google.maps.Circle({
            strokeColor: '#0000FF',
            strokeOpacity: 0.25,
            strokeWeight: 2,
            fillColor: '#0000FF',
            fillOpacity: 0.25,
            map: map,
            center: trip[point].center,
            radius: 30
          });
        }
      }
    </script>
    <script async defer
    src="https://maps.googleapis.com/maps/api/js?key=AIzaSyBlabwKhgVWHc5Yfr3bUYGSUDJyYTKX5QY&callback=initMap">
    </script>
  </body>
</html>

"""
class Runner(object):
    """
    A collection of utilities to process the SHED10 data.  The approach taken
    here was to download the required tables into CSV files then post-process
    them, rather than to perform complicated SQL queries.  Generate lots of
    intermediate files for plotting (e.g., before aggregation, etc)
    """

    def __init__(self):

        self._myproj = pyproj.Proj("+init=EPSG:32613")


    def list_gps_users(self):
        line_count = 0
        f = open("../maup/gps_utm.csv")
        user_dict = {}

        line = ''

        try:
            for line in f:
                line_count += 1
                if line_count == 1: continue
                parts = line.split(",")
                user_id = int(parts[0].strip())

                count = user_dict.get(user_id, 0)
                count += 1
                user_dict[user_id] = count

        except Exception as err:

            print "Exception: %s" % err
            print "Line: %s" % line

        finally:
            f.close()


        for user_id, count in user_dict.iteritems():
            print "User ID: %d GPS points: %d" %(user_id, count)

    def find_points_near_stops(self, user_id=None, radius=None):

        stop_point_dict = {}

        f = open('data/bus_stops.json', 'r')
        bus_stops = simplejson.load(f)
        f.close()

        line_count = 0
        f = open("../maup/gps_utm.csv")

        for line in f:
            line_count += 1
            if line_count == 1: continue
            parts = line.split(",")
            user_id_gps = int(parts[0].strip())

            if user_id_gps != user_id:
                continue

            x = float(parts[1].strip())
            y = float(parts[2].strip())
            sec = int(parts[3].strip())

            for stop_index, d in bus_stops.iteritems():
                stop_x = d.get('x')
                stop_y = d.get('y')

                dist = self.get_dist((x, y), (stop_x, stop_y))

                if dist < radius:
                    print "point is near stop: %s" % d.get('name')
                    key = "%d (%s)" % (int(stop_index), d.get('name'))

                    stop_data = stop_point_dict.get(key, {})
                    stop_points = stop_data.get('points', [])
                    stop_points.append((x, y, sec))
                    stop_data['points'] = stop_points
                    stop_data['name'] = d.get('name')
                    stop_data['index'] = stop_index
                    stop_data['x'] = stop_x
                    stop_data['y'] = stop_y
                    stop_point_dict[key] = stop_data

        f.close()

        file_name = "data/user_radius_%d_%d.json" % (user_id, radius)

        f = open(file_name, 'w')
        simplejson.dump(stop_point_dict, f, indent=4)
        f.close()

    def check_user_stops(self, user_id=None, radius=None):

        file_name = "data/user_radius_%d_%d.json" % (user_id, radius)

        f = open(file_name, 'r')
        stop_data_points = simplejson.load(f)
        f.close()

        for key, value in stop_data_points.iteritems():
            stop_points = value.get('points')
            print "Stop: %s points: %d" % (key, len(stop_points))

    def make_stop_map(self, user_id=None, radius=None, stop_index=None):

        from map_stop import TOP as MAP_TOP
        from map_stop import BOTTOM as MAP_BOTTOM
        from map_stop import CIRCLE1, CIRCLE2

        file_name = "data/user_radius_%d_%d.json" % (user_id, radius)

        f = open(file_name, 'r')
        stop_data_points = simplejson.load(f)
        f.close()

        stop_points = None

        for key, value in stop_data_points.iteritems():
            stop_index_this = int(value.get('index'))
            if stop_index_this == stop_index:
                stop_points = value.get('points')
                break

        if stop_points is None:
            print "No GPS points detected"

        map_name = "maps/map_user_radius_stop_%d_%d_%d.html" % (user_id, radius, stop_index)

        f = open(map_name, "w")
        f.write(MAP_TOP)
        f.write("var circle1 = {\n")

        stop_x = value.get('x')
        stop_y = value.get('y')

        lon, lat =  self._myproj(stop_x, stop_y, inverse=True)

        f.write("%d: {center:{lat: %f, lng: %f},},\n" % (0, lat, lon))
        f.write("};\n")
        f.write(CIRCLE1)

        f.write("var circle2 = {\n")
        for i, point in enumerate(stop_points):

            lon, lat = self._myproj(point[0], point[1], inverse=True)
            f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))

        f.write("};\n")
        f.write(CIRCLE2)

        f.write(MAP_BOTTOM)

        f.close()

    def make_bus_stops(self):

        result = {}
        index = 0

        line_count = 0
        f = open("data/TransitStops.csv")
        for line in f:
            line_count += 1
            if line_count == 1: continue
            parts = line.split(",")
            name = parts[3].strip()
            lat = float(parts[5].strip())
            lon = float(parts[6].strip())
            print lat, lon, name

            x, y  = self._myproj(lon, lat)
            stop_data = {
                'lat' : lat,
                'lon' : lon,
                'x' : x,
                'y' : y,
                'name' : name
            }

            result[index] = stop_data
            index += 1
        f.close()

        f = open('data/bus_stops.json', 'w')
        simplejson.dump(result, f, indent=4)
        f.close()


    def make_bus_files(self):
        """
        Read in all the battery records and count according to user ID.
        Compute percentage of total returned by each user, and make a
        list of those above a threshold and those below a threshold.
        """
        route_dict = {}

        line_count = 0
        f = open("data/TransitShapes.csv", "r")


        for line in f:
            line_count += 1
            if line_count == 1: continue

            line = line.strip()
            parts = line.split(",")

            route_id = int(parts[1].strip())
            lat = float(parts[2].strip())
            lon = float(parts[3].strip())
            seq = int(parts[4].strip())
            dist = float(parts[5].strip())

            x, y  = self._myproj(lon, lat)

            # test_lon, test_lat = self._myproj(x, y, inverse=True)
            # print lon, test_lon, lat, test_lat

            route_data = route_dict.get(route_id, [])

            route_data.append((seq, x, y, dist))
            route_dict[route_id] = route_data

        f.close()

        repeat_dict = {}
        new_dict = {}

        for route_id, route_data in route_dict.iteritems():
            sum_x = 0
            for item in route_data:
                sum_x += item[1]

            key = "%d-%d" % (len(route_data), int(sum_x))

            if repeat_dict.has_key(key):
                print "DUPLICATE ROUTE DETECTED!!"
                continue

            new_dict[route_id] = route_data
            repeat_dict[key] = True

            print "id: %d points: %d sum_x: %f" % (route_id, len(route_data), sum_x)

        route_dict = new_dict

        new_dict = {}
        route_count = 0
        for route_id, route_data in route_dict.iteritems():
            print "count: %d id: %d points: %d" % (route_count, route_id, len(route_data))
            # self.make_route_file(route_id, route_data)

            route_data = self.trip_fill(route_data)
            new_dict[route_id] = route_data
            self.make_route_file(route_id, route_data)

        f = open('data/bus_routes.json', 'w')
        simplejson.dump(new_dict, f, indent=4)
        f.close()

    def trip_fill(self, route_data):
        # Sort the data.  Sequence is first item

        sort_list = [(item[0], (item[1], item[2])) for item in route_data]
        s = sorted(sort_list)
        route_data = [item[1] for item in s]

        print "points", len(route_data)
        while True:

            points_added = 0
            filled_route = []

            points = len(route_data)
            for i in xrange(points - 1):
                point1 = route_data[i]
                point2 = route_data[i+1]

                dist = self.get_dist(point1, point2)
                # print point1, point2, dist

                # Add first point to route
                filled_route.append(point1)
                if dist > 25:
                    new_point = self.insert_point(point1, point2)
                    filled_route.append(new_point)
                    points_added += 1

            # Must add last point when we break out of loop
            filled_route.append(point2)

            route_data = filled_route
            print "points", len(route_data), "Added", points_added

            if points_added == 0:
                break

        return route_data

    def insert_point(self, point1, point2):

        x1 = point1[0]
        y1 = point1[1]
        x2 = point2[0]
        y2 = point2[1]

        new_x = x1 + (x2 - x1)/2.0
        new_y = y1 + (y2 - y1)/2.0

        return (new_x, new_y)

    def get_dist(self, point1, point2):

        if point1 is None or point2 is None: return 0.0

        x1 = point1[0]
        y1 = point1[1]
        x2 = point2[0]
        y2 = point2[1]

        if x1 is None or x2 is None: return 0.0

        return math.sqrt(math.pow((x1 - x2), 2) + math.pow((y1 - y2),2))

    def make_route_file(self, route_id, route_data):

        file_name = "data/route_points_%06d.csv" % route_id

        f = open(file_name, "w")
        f.write("index, utm_x, utm_y, dist\n")

        point_count = 0
        point_prev = None
        for point in route_data:
            point_count += 1
            sep = self.get_dist(point, point_prev)
            point_prev = point
            f.write("%d,%f,%f,%f\n" % (point_count, point[0], point[1], sep))

        f.close()

    def get_trip_points(self, file_name):

        f = open(file_name, "r")
        line_count = 0
        total_distance = 0
        time_sec = []


        prev_x = None
        prev_y = None

        points_list = []
        for line in f:

            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            x = float(parts[0].strip())
            y = float(parts[1].strip())
            sec = int(parts[2].strip())

            time_sec.append(sec)

            points_list.append((x, y))

            distance = self.get_dist((prev_x, prev_y), (x, y))

            prev_x = x
            prev_y = y

            total_distance += distance
            # print "dist, total_dist", distance, total_distance

        f.close()

        duration = max(time_sec) - min(time_sec)

        speed_ms = float(total_distance)/float(duration)
        print "speed m/s", speed_ms

        speed_kph = 3600.0 * speed_ms / 1000.0
        print "speed_kph", speed_kph

        return points_list, speed_kph, duration, total_distance

    def compare_one_trip(self, file_name, bus_routes):

        trip_points, speed_kph, duration, trip_dist = self.get_trip_points(file_name)
        print "number of points", len(trip_points)

        count = 0
        result = []

        for route_id, route_data in bus_routes.iteritems():

            closest_list = numpy.zeros((len(trip_points,)), dtype=float)

            for i, point in enumerate(trip_points):

                closest_dist = 99999999999
                for route_point in route_data:
                    dist = self.get_dist(point, route_point)
                    if dist < closest_dist:
                        closest_dist = dist

                closest_list[i] = closest_dist

            ave_dist = numpy.average(closest_list, axis=0)
            # print closest_list
            print "Compare trip %s to route %s dist %f" %(file_name, repr(route_id), ave_dist)
            result.append((ave_dist, route_id))

        result = sorted(result)

        for item in result:
            print "Route ID: %s Ave Dist: %s" % (repr(item[1]), repr(item[0]))

        print "Speed (km/h): %f Duration: %d" % (speed_kph, duration)

        if len(result) > 0:
            item = result[0]
            route_id = item[1]
            ave_dist = item[0]

            f = open("data/closest_routes.csv", "a")
            f.write("%s, %s, %0.2f ave dist(m), %0.2f trip dist (m), %0.2f km/h, %d sec\n" % \
                    (file_name, repr(route_id), ave_dist, trip_dist, speed_kph, duration))
            f.close()

    def compare_trips_to_routes(self):

        f = open('data/bus_routes.json', 'r')
        bus_routes = simplejson.load(f)
        f.close()

        for route_id in bus_routes.iterkeys():
            print "route_id", route_id

        for item in scandir.scandir('../maup/user_trips'):
            if item.is_file():
                if item.name.startswith('user_trip_'):
                    self.compare_one_trip(item.path, bus_routes)

    def make_google_maps_file(self, file_name, file_trip):
        """
        1: { center: {lat: 52.878, lng: -106.629},},
        2: { center: {lat: 52.714, lng: -106.7005},},
        3: { center: {lat: 52.052, lng: -106.7243},},
        4: { center: {lat: 52.25, lng: -106.71},}
        """

        f = open(file_name, "r")
        line_count = 0

        path = []

        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            utm_x = float(parts[1].strip())
            utm_y = float(parts[2].strip())

            lon, lat =  myProj(utm_x, utm_y, inverse=True)
            path.append((lat, lon))

        f.close()

        #############################
        f = open(file_trip, "r")
        line_count = 0

        trip = []

        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            utm_x = float(parts[0].strip())
            utm_y = float(parts[1].strip())

            print "trip parts", parts

            lon, lat =  myProj(utm_x, utm_y, inverse=True)
            trip.append((lat, lon))

        f.close()

        ##################################

        f = open("data/map.html", "w")
        f.write("%s\n" % TOP)

        for item in path:
            f.write("{lat: %f, lng: %f},\n" % (item[0], item[1]))

        # 1: { center: {lat: 52.878, lng: -106.629},},
        f.write("%s\n" % MIDDLE)

        for i, item in enumerate(trip):
            f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, item[0], item[1]))

        f.write("%s\n" % BOTTOM)

if __name__ == "__main__":


    runner = Runner()

    #runner.list_gps_users()
    # runner.make_bus_stops()
    # runner.make_bus_files()


    #runner.find_points_near_stops(user_id=555, radius=100)
    #runner.check_user_stops(user_id=555, radius=100)
    runner.make_stop_map(user_id=555, radius=100, stop_index=660)

    #runner.find_points_near_stops(user_id=513, radius=100)
    #runner.check_user_stops(user_id=513, radius=100)
    #runner.make_stop_map(user_id=513, radius=100, stop_index=1069)

    #runner.find_points_near_stops(user_id=1301, radius=100)
    #runner.check_user_stops(user_id=1301, radius=100)
    #runner.make_stop_map(user_id=1301, radius=100, stop_index=34)

    #runner.compare_trips_to_routes()
    #.make_google_maps_file("data/route_points_050410.csv", "../maup/user_trips/user_trip_1301_15.csv")
    
    #runner.make_google_maps_file("data/route_points_050005.csv", "../maup/user_trips/1323/user_trip_1323_23.csv")
    # ../maup/user_trips/user_trip_559_104.csv, '50402', 27.13 ave dist(m), 7775.15 trip dist (m), 16.89 km/h, 1657 sec

    # runner.make_google_maps_file("data/route_points_050402.csv", "../maup/user_trips/user_trip_559_104.csv")

