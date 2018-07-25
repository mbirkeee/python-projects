import shapefile
import pyproj
import csv
import StringIO

from my_utils import DaCentriods


from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import POLYGON, POLYLINE

from map_html import CIRCLE1, CIRCLE2
from map_html import CIRCLE_RED_20, CIRCLE_RED_50

import settings


class Runner(object):

    def __init__(self):

        self._myproj = pyproj.Proj("+init=EPSG:32613")

        self._data_pop_by_da = {}
        self._centroids = {}
        self._test_polygon = []

        self._route_dict = {}
        self._stop_dict = {}
#        self._route_id_dict = {}

        self._shape_base = "../data/shapefiles/brt_lines/brt"
        # self._shape_base = "../data/shapefiles/brt_lines/existing"

    # def load_stats_can_pop_data(self):
    #
    #     f = open("../data/2016_pop.csv", "r")
    #
    #     expected_parts = 15
    #
    #     for line in f:
    #         # print "LINE", line.strip()
    #         parts = line.split(",")
    #         # print len(parts)
    #
    #         if len(parts) != 15:
    #             print "BAD LINE!!!!!", line
    #             print len(parts)
    #             continue
    #
    #         try:
    #             da_id = int(parts[1].strip('"'))
    #             pop = int(parts[12].strip('"'))
    #         except Exception as err:
    #             print "Failed for line:", line
    #             continue
    #             # raise ValueError("unexpected number of parts")
    #
    #         print "ID:", da_id, "POP:", pop
    #
    #         if self._data_pop_by_da.has_key(da_id):
    #             raise ValueError("Already have da_id: %s" % da_id)
    #
    #         self._data_pop_by_da[da_id] = pop
    #
    #     f.close()

    # def make_da_cvs_from_text(self):
    #
    #     f = open("da_test.txt")
    #     count = 0
    #
    #     f2 = open("da_population.csv", "w")
    #     f2.write("FID,DAUID,da_feature_id,population\n")
    #
    #     for line in f:
    #         count += 1
    #         if count == 1: continue
    #
    #         parts = line.split(",")
    #         print parts
    #
    #         try:
    #             da_id = int(parts[1].strip())
    #             da_fid = int(parts[23].strip())
    #             lat = float(parts[24].strip())
    #             lon = float(parts[25].strip())
    #         except:
    #             print "BAD LINE", line
    #             continue
    #
    #         print da_id, da_fid, lat, lon
    #
    #         population = self._data_pop_by_da.get(da_id)
    #         if population is None:
    #             raise ValueError("Failed tpo get pop for %s" % repr(da_id))
    #
    #         f2.write("%d,%d,%d,%d\n" % (count-1, da_id, da_fid, population))
    #         self._centroids[da_id] = {
    #         #     'x' : x,
    #         #     'y' : y,
    #             'lat' : lat,
    #             'lon' : lon
    #         }
    #
    #     f.close()
    #     f2.close()



    def read_direction_stops_old(self):
        sf = shapefile.Reader("%s/direction_stops.dbf" % self._shape_base, "rb")
        records = sf.records()
        shapes = sf.shapes()

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for index, record in enumerate(records):
            shape = shapes[index]
            print repr(record)

    def read_direction_stops(self):

        """
        ['1424e21', 'HDR Future Network V3', '4174', 'Superstore',
        "10 Mainline, Confederation - Centre Mall (Inbound),
        14 Crosstown, St Paul's (Outbound),
        3 BRT, Green (Inbound),
        48 Suburban Connector, 33rd St - Confed (Inbound)"]
        """
        line_count = 0

        temp_dict = {}

        f = open("%s/test.out" % self._shape_base, 'rb')
        for line in f:
            # print line
            line_count += 1

            if line_count == 2:

                #line.replace("Mall", "")

                parts = line.split()
                print "PARTS: %d" % len(parts)

                part_index = 1

                while True:

                    try:
                        dir_id = parts[part_index].strip()
                        stop_id = parts[part_index + 1].strip()
                        if stop_id == "Market":
                            part_index += 1

                        dist = parts[part_index + 2].strip()

                    except:
                        print "Done"
                        break

#                    print "dir_id", dir_id, "stop_id", stop_id, "dist", dist
                    part_index += 3


                    stop_list = temp_dict.get(dir_id, [])
                    stop_list.append(stop_id)
                    temp_dict[dir_id] = stop_list

                    if stop_id == '4174':
                        print "4174 on route", self.get_route_name_from_id(dir_id)


                # part_index = 0
                # for part in parts:
                #     print "part: %d: >>%s<<" % (part_index, part.strip())
                #     part_index += 1
                #     if part_index > 50:
                #         break

        f.close()

        for route_id, stop_list in temp_dict.iteritems():
            route_data = self._route_dict.get(route_id)
            if route_data is None:
                raise ValueError("failed to get route: %s" % route_id)
            route_data['stops'] = stop_list
            self._route_dict[route_id] = route_data

            #print "Name: %s stops: %d" % (route_data.get('name'), len(stop_list))
        x = [(route_id, route_data) for route_id, route_data in self._route_dict.iteritems()]
        x = sorted(x)

        for item in x:
            route_data = item[1]
            print "Name: %s Stops: %d" % (route_data.get('name'), len(route_data.get('stops')))
        print "number of routes", len(x)

    def read_directions(self):

        sf = shapefile.Reader("%s/directions.dbf" % self._shape_base)

        records = sf.records()
        shapes = sf.shapes()

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for index, record in enumerate(records):
            shape = shapes[index]

#            print repr(record)
            # continue

            name = record[5]
            direction = record[2].strip().lower()
            display_name = "%s (%s)" % (name.strip(), direction)
            route_id = record[1]

#            print "ROUTE_ID", route_id
#            print "LINE:", display_name, route_id


#            name_parts = name.split(",")
#            print "name part 0", name_parts[0]

            # try:
            #     print "name part 1", name_parts[1]
            # except:
            #     pass
            #
            # # print "direction", direction
            # # continue
            #
            # if direction == "inbound":
            #     dir_code = 0
            # elif direction == "outbound":
            #     dir_code = 1
            # elif direction == 'ccw':
            #     dir_code = 0
            # elif direction == 'cw':
            #     dir_code = 1
            # else:
            #     raise ValueError("BAD DIRECTION!!!")

#            route_key = "%s-%d" % (name_parts[0].strip().lower(), dir_code)

#            if self._route_dict.has_key(route_key):
            if self._route_dict.has_key(route_id):
                raise ValueError("Already have route key")

            self._route_dict[route_id] = {
                'name' : display_name,
#                "id" : route_id,
                "direction" : direction,
                "points" : shape.points
            }
            # print repr(shape)
            # print dir(shape)

            # print "len(shape.points)", len(shape.points)

            # for point in shape.points:
            #     print point

            #self.plot_brt_route(name, direction, shape.points)

        for key, value in self._route_dict.iteritems():
            print value.get('name')

       # for key, value in self._route_id_dict.iteritems():
       #     print "KEY: %s VALUE: %s" % (key, value)

    def plot_brt_routes(self):
        for value in self._route_dict.itervalues():
            name = value.get('name')
            route_id = value.get('id')
            direction = value.get('direction')
            points = value.get('points')
            stops = value.get('stops')
            self.plot_brt_route(name, direction, points, stops)

    def plot_brt_route(self, name, direction, points, stop_ids):

        file_name = "%s/maps/brt_route_%s.html" % (settings.TEMP_DATA_BASE, name)
        file_name = file_name.replace(",", "")
        file_name = file_name.replace("(", "_")
        file_name = file_name.replace(")", "_")
        file_name = file_name.replace(" ", "_")
        file_name = file_name.replace("-", "")
        file_name = file_name.replace("__", "_")
        file_name = file_name.replace("__", "_")

        print "making map file", file_name

        f = open(file_name, "w")
        f.write(MAP_TOP)

        f.write("var polyline = [\n")

        i = 0
        for point in points:
            lon = point[0]
            lat = point[1]
            f.write("{lat: %f, lng: %f},\n" % (lat, lon))
            i += 1

        f.write("];\n")
        f.write(POLYLINE)

        f.write("var circle = {")
        i = 0


        for stop_id in stop_ids:
            print "Adding stop", stop_id
            lat, lon = self.get_stop_lat_lon(stop_id)
            f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lon))
            i += 1
            if i > 10: break

        f.write("};\n")
        f.write(CIRCLE_RED_50)

        f.write(MAP_BOTTOM)
        f.close()

    # def read_stops_old(self):
    #
    #     line_dict = {}
    #
    #     LINE_NAME_MAP = {
    #         "1 BRT" : "1 BRT (Red)",
    #         "2 BRT" : "2 BRT (Blue)",
    #         "3 BRT" : "3 BRT (Green)",
    #     }
    #
    #     sf = shapefile.Reader("%s/stops.dbf" % self._shape_base)
    #     records = sf.records()
    #     shapes = sf.shapes()
    #
    #     print "len(records)", len(records)
    #     print "len(shapes)", len(shapes)
    #
    #     f = open("temp_data/brt_stops.csv", "w")
    #
    #     f.write("index,stop_id,stop_name,lat,lng,on_red,on_green,on_blue\n")
    #     stop_index = 0
    #
    #     for index, record in enumerate(records):
    #         print repr(record)
    #
    #         shape = shapes[index]
    #
    #         # print "len(shape.points)", len(shape.points)
    #         # print shape.points
    #
    #         point = shape.points[0]
    #         lat = point[1]
    #         lng = point[0]
    #         # print lat, lng
    #
    #         #continue
    #
    #         stop_id = record[3]
    #         stop_name = record[2]
    #         lines = record[4]
    #
    #         print stop_id, stop_name, lines
    #         print "LINES", lines
    #
    #         parts = lines.split(',')
    #         print "LINE PARTS:", len(parts)
    #
    #         if len(parts) == 1:
    #             if len(parts[0].strip()) != 0:
    #                 raise ValueError("what the??")
    #             print "skip stop"
    #             continue
    #
    #         if len(parts) % 2:
    #
    #             raise ValueError("Odd number of parts!!!")
    #
    #         line_list = []
    #         on_red = False
    #         on_green = False
    #         on_blue = False
    #
    #         for i in xrange(len(parts)/2):
    #             line = "%s: %s" % (parts[i * 2].strip(), parts[1+ i * 2].strip())
    #             print "LINE: %s" % line
    #
    #             if line.find(" Red ") > 0:
    #                 print "ON RED LINE"
    #                 on_red = True
    #
    #             if line.find(" Green ") > 0:
    #                 print "ON GREEN LINE"
    #                 on_green = True
    #
    #             if line.find(" Blue ") > 0:
    #                 print "ON BLUE LINE"
    #                 on_blue = True
    #
    #             count = line_dict.get(line, 0)
    #             count += 1
    #             line_dict[line] = count
    #             line_list.append(line)
    #
    #
    #         if not on_green and not on_blue and not on_red:
    #             continue
    #
    #         print "TEST123", stop_index, stop_name, stop_id
    #
    #         f.write("%d,%s,%s,%f,%f,%s,%s,%s\n" % (stop_index, stop_id, stop_name, lat, lng, on_red, on_green, on_blue))
    #         stop_index += 1
    #
    #     f.close()
    #
    #     x = [(key, value) for key, value in line_dict.iteritems()]
    #     x = sorted(x)
    #
    #     for item in x:
    #         print "%s -------> %d" % (item[0], item[1])

    def get_route_name_from_id(self, route_id):
        data = self._route_dict.get(route_id)
        if data is None:
            raise ValueError("No route_id: %s" % repr(route_id))

        return data.get('name')

    def read_stops_new(self):

        line_dict = {}

        skipped_stops = 0
        active_stops = 0

        sf = shapefile.Reader("%s/stops.dbf" % self._shape_base)
        records = sf.records()
        shapes = sf.shapes()

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for index, record in enumerate(records):
            print repr(record)
#            continue

            shape = shapes[index]

            # print "len(shape.points)", len(shape.points)
            # print shape.points

            point = shape.points[0]
            lat = point[1]
            lng = point[0]
            # print lat, lng

            stop_id = record[2]
            stop_name = record[3]
            lines = record[4]

            # print stop_id, stop_name, lines
            lines = lines.strip()
            # print "LINES >>>%s<<<" % lines

            parts = lines.split(',')
            # print "LINE PARTS:", len(parts)

            stop_data = {
                'name' : stop_name,
                'lat' : float(lat),
                'lng' : float(lng),
            }

            if self._stop_dict.has_key(stop_id):
                raise ValueError("already have stop id: %s %d" % (repr(stop_id), index))

            self._stop_dict[stop_id] = stop_data


        print "stops skipped:", skipped_stops
        print "stops active:", active_stops


    def get_stop_lat_lon(self, stop_id):
        value = self._stop_dict.get(stop_id)
        lat = value.get('lat')
        lng = value.get('lng')
        return lat, lng

    def read_shapefile(self):

        sf = shapefile.Reader("../data/shapefiles/DA_centriods/Da_CentroidPoints.dbf")
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for i in xrange(len(records)):
            record = records[i]
            shape = shapes[i]

            print repr(record)

            print "len(shape.points)", len(shape.points)
            print shape.points

            point = shape.points[0]

            # da_id = int(record[0])
            # da_fid = int(record[22])
            # x = point[0]
            # y = point[1]
            #
            # population = self._data_pop_by_da.get(da_id)
            # if population is None:
            #     raise ValueError("Failed tpo get pop for %s" % repr(da_id))
            #
            # line =  "%d,%d,%d,%f,%f,%d" % (i+1, da_id, da_fid, x, y, population)
            # f.write("%s\n" % line)
            #
            # lon, lat =  self._myproj(x, y, inverse=True)
            #
            # self._centroids[da_id] = {
            #     'x' : x,
            #     'y' : y,
            #     'lat' : lat,
            #     'lon' : lon
            # }

        print dir(sf)

        # f.close()
            # if i > 10: break

    def make_example_polygons(self):

        center_lat = 52.125
        center_lng = -106.650

        center_x, center_y = self._myproj(center_lng, center_lat)

        poly_points = [
            (-50, 0),
            (0, 50),
            (50, 0),
            (0, -50),
            (-50, 0)
        ]

        for i in xrange(len(poly_points)):
            start_point = poly_points[i]

            start_x = center_x + start_point[0]
            start_y = center_y + start_point[1]

            print ((start_x, start_y))
            self._test_polygon.append((start_x, start_y))

    def plot(self):
        pass
        # centriods = DaCentriods()
        # centriod_dict = centriods.get_centriods()
        #
        map_name = "data/maps/test_polygon.html"

        f = open(map_name, "w")

        f.write(MAP_TOP)
        f.write("var polypoints = [\n")

        i = 0
        for start in self._test_polygon:

            print "ADDING DOT TO PLOT!!!!", repr(start)
            start_x = start[0]
            start_y = start[1]
            lon, lat = self._myproj(start_x, start_y, inverse=True)
            f.write("{lat: %f, lng: %f},\n" % (lat, lon))
            i += 1

        f.write("];\n")

        f.write(POLYGON % 0.1)

        f.write("var polypoints = [\n")
        i = 0
        for start in self._test_polygon:

            print "ADDING DOT TO PLOT!!!!", repr(start)
            start_x = start[0] + 100.
            start_y = start[1] + 100.0
            lon, lat = self._myproj(start_x, start_y, inverse=True)
            f.write("{lat: %f, lng: %f},\n" % (lat, lon))
            i += 1

        f.write("];\n")
        f.write(POLYGON % 0.3)


        f.write("var polypoints = [\n")
        i = 0
        for start in self._test_polygon:

            print "ADDING DOT TO PLOT!!!!", repr(start)
            start_x = start[0] + 200.
            start_y = start[1] + 200.0
            lon, lat = self._myproj(start_x, start_y, inverse=True)
            f.write("{lat: %f, lng: %f},\n" % (lat, lon))
            i += 1

        f.write("];\n")
        f.write(POLYGON % 0.5)
        f.write(MAP_BOTTOM)
        f.close()
        print "Wrote MAP file: %s" % map_name

if __name__ == "__main__":

    """
    HDR Network: https://platform.remix.com/map/1424e21/line/fbf0675?pat=A&dir=1
    JANE: https://platform.remix.com/map/7445e73/line/ef79fbc?pat=C&dir=0

    """
    runner = Runner()
    #runner.read_stops()

    runner.read_directions()
    runner.read_stops_new()
    runner.read_direction_stops()

#    runner.plot_brt_routes()

    # runner.read_test()

    # runner.read_direction_stops()

    # runner.make_example_polygons()
    # runner.plot()
    # runner.load_stats_can_pop_data()
    # runner.read_shapefile()

    # runner.make_da_cvs_from_text()



