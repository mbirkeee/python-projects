import shapefile

from plotter import Plotter
from plotter import ATTR

from geometry import Point
from geometry import Polygon
from geometry import Polypoint

class Runner(object):

    def __init__(self):

        self._postal_codes = self.load_postal_codes("data/csv/interact_users_2018_09_24.csv")

    def load_postal_codes(self, filename):

        result = {}

        line_count = 0
        f = open(filename, "r")
        for line in f:
            line_count +=1
            if line_count == 1: continue
            code = line.strip()

            count = result.get(code, 0)
            count += 1
            result[code] = count

        f.close()

        for k, v in result.iteritems():
            print k, v

        return result

    def run(self):

        plotter = Plotter()
        file_name = "data/shapefiles/postal_codes/Postal_Codes_Polygons_Nov-2012.shp"

        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        print "number of records:", len(records)

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        match_count = 0
        match_list = []

        user_points = Polypoint()

        fout = open("interact_user_locations_2018_09_24.csv", "w")
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
                print "%s: FOUND" % k
            else:
                print "%s: NOT FOUND" % k

        print "match_count", match_count

if __name__ == "__main__":

    runner = Runner()
    runner.run()
