import shapefile

from plotter import Plotter
from plotter import ATTR

from geometry import Point
from geometry import Polygon
from geometry import Polypoint

class Runner(object):

    def __init__(self):

        self._rider = {}
        self._postal_codes = self.load_user_postal_codes("data/csv/interact_users_2018_11_26.csv")
        self._pc_dict = self._postal_code_txt_to_csv("data/csv/pcc_saskatoon_062017.txt", "data/csv/postal_codes_centroids_2017.csv")


    def _to_numeric(self, input):

        result = ""
        for c in input:
            if c.isdigit() or c == '.' or c == '-':
                result += c

        return result

    def _postal_code_txt_to_csv(self, filename_in, filename_out):
        """
        Read in the raw postal code txt file from the post office.  Assume that it
        has already been grepped for SASKATOON.

        Write the cleaned results into a CVS file
        """

        pc_dict = {}

        fin = open(filename_in, "r")
        # fout = open(filename_out, "w")

        for line in fin:
            line = line.strip()
            # print line
            parts = line.split()
            # print parts

            postal = parts[0]
            postal_part1 = postal[:3]
            postal_part2 = postal[3:6]
            lat = float(self._to_numeric(parts[3]))
            lng = float(self._to_numeric(parts[4]))

            # print postal_part1, postal_part2

            postal_code = postal_part1 + " " + postal_part2

            # print postal_code, lat, lng

            points = pc_dict.get(postal_code, [])
            points.append((lat, lng))
            pc_dict[postal_code] = points

        fin.close()

        fout = open(filename_out, "w")

        fout.write("fid,postal_code,lat,lng\n")

        index = 1
        for k, v in pc_dict.iteritems():
            for item in v:
                print k, item
                fout.write("%d,%s,%f,%f\n" % (index, k, item[0], item[1]))
                index += 1
            # print k, len(v)
        fout.close()

        print len(pc_dict)
        return pc_dict

    def load_user_postal_codes(self, filename):

        result = {}

        line_count = 0
        user_count = 0
        f = open(filename, "r")
        for line in f:
            line_count +=1
            if line_count == 1: continue

            line=line.strip(",")

            line = line.strip()
            parts = line.split(",")
            if len(parts) != 2:
                print "SKIPPING LINE", line
                continue

            rider = parts[0].strip()
            code = parts[1].strip()
            code = code.strip(',')

            if len(code) == 6:
                code = "%s %s" % (code[0:3], code[3:6])
                print "CODE!!!!!!", code

            if len(code) == 0: continue

            if rider == "Yes":
                rider_count= self._rider.get(code, 0)
                rider_count += 1
                self._rider[code] = rider_count

            count = result.get(code, 0)
            count += 1
            result[code] = count
            user_count += 1
        f.close()

        print "---"
        for k, v in result.iteritems():
            print k, v
        print "---", user_count

        # raise ValueError("temp stop")

        return result

    def run_new(self):
        """
        Use the latest postal code data.  Note that some postal codes
        have multiple GPS positions... use centroid
        """
        plotter = Plotter()
        locations = Polypoint()

        fout = open("interact_user_locations_2018_11_26.csv", "w")
        fout.write("fid,rider,lat,lng\n")
        fid = 0

        for user_postal_code, count in self._postal_codes.iteritems():
            print "user postal code", user_postal_code, count

            location = self._pc_dict.get(user_postal_code)
            if location is None:
                print "NOT FOUND: %s" % user_postal_code
                # raise ValueError("not found")
                continue

            ppoint = Polypoint()
            for p in location:
                ppoint.add_point(Point(p[0], p[1]))

            centroid = ppoint.get_centroid()

            rider_count = self._rider.get(user_postal_code, 0)
            print "rider_count", rider_count

            for x in xrange(count):
                y_move = int(x/2)
                x_move =  x - y_move * 2
                # print x_move, y_move

                point = Point(centroid.get_x() + 100 * x_move, centroid.get_y() + 100 * y_move)
                locations.add_point(point)

                if rider_count > 0:
                    rider = "Yes"
                else:
                    rider = "No"

                rider_count  -= 1
                fout.write("%d,%s,%f,%f\n" %(fid, rider, point.get_lat(), point.get_lng()))
                fid += 1

            locations.add_point(centroid)

        locations.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        locations.set_attribute(ATTR.FILL_OPACITY, 1.0)

        fout.close()
        plotter.add_polypoint(locations)
        plotter.plot("temp/maps/postal.html")


    def run(self):


        plotter = Plotter()
        file_name = "data/shapefiles/postal_codes/Postal_Codes_Polygons_Nov-2012.shp"

        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        print "number of records:", len(records)

        raise ValueError("temp stop")

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        match_count = 0
        match_list = []

        user_points = Polypoint()

        fout = open("interact_user_locations_2018_10_01.csv", "w")
        fout.write("fid,lat,lng\n")
        fid = 0

        for i, record in enumerate(records):
            # print repr(record)
            postal_code = record[0].strip()
            # print "POSTAL CODE", postal_code
            shape = shapes[i]
            polygon = Polygon()

            # print stop_id, len(shape.points)
            if len(shape.points) < 4:
                raise ValueError("not enough points!!!")

            start_point = None
            for index in xrange(len(shape.points)):
                item = shape.points[index]
                if start_point is None:
                    start_point = (item[0], item[1])
                else:
                    if item[0] == start_point[0] and item[1] == start_point[1]:
                        break
                polygon.add_point(Point(item[0], item[1]))

            count = self._postal_codes.get(postal_code)
            if count > 0:
                match_count +=1
                match_list.append(postal_code)

                centroid  = polygon.get_centroid()

                for x in xrange(count):
                    point = Point(centroid.get_x() + 100 * x, centroid.get_y())
                    user_points.add_point(point)
                    fout.write("%d,%f,%f\n" %(fid, point.get_lat(), point.get_lng()))
                    fid += 1

            plotter.add_polygon(polygon)
            # for index in xrange(len(shape.points)-1):
            #     item = shape.points[index]
            #     polygon.add_point(Point(item[0], item[1]))

        fout.close()
        user_points.set_attribute(ATTR.FILL_COLOR, "#0000ff")
        user_points.set_attribute(ATTR.FILL_OPACITY, 1.0)

        plotter.add_polypoint(user_points)

        plotter.plot("temp/maps/postal.html")

        match_list = list(set(match_list))

        for k, v in self._postal_codes.iteritems():
            if k in match_list:
                print "%s: FOUND" % k, v
            else:
                print "%s: NOT FOUND" % k, v

        print "match_count", match_count

if __name__ == "__main__":

    runner = Runner()
    runner.run_new()
    # runner.run()
