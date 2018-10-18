import os
import shapefile

from geometry import Point
from geometry import Polygon

from shapefile_writer import ShapeFileWriter

RASTER_SHAPEFILE_TEMPLATE = "temp/shapefiles/raster_cache/%s/da_id_%d.shp"

class Raster(object):

    def __init__(self, parent_id, my_id, polygon):

        self._my_id = my_id
        self._parent_id = parent_id
        self._polygon = polygon
        self._score = 0
        self._centroid = None

    def set_score(self, score):
        self._score = score

    def get_score(self):
        return self._score

    def get_id(self):
        return self._my_id

    def get_parent_id(self):
        return self._parent_id

    def get_polygon(self):
        return self._polygon

    def get_centroid(self):
        if self._centroid is None:
            self._centroid = self._polygon.get_centroid()
        return self._centroid

    def get_closest_stop(self, stops, method='crow'):

        min_dist = None
        min_stop = None

        centroid = self.get_centroid()

        for stop in stops:
            distance = centroid.get_distance(stop.get_point(), method=method)

            if min_dist is None or distance < min_dist:
                min_dist = distance
                min_stop = stop

        return min_dist, min_stop


class DA(object):

    def __init__(self, da_id):
        self._da_id = da_id
        self._point_dict = {}
        self._polygon = None
        self._clipped_polygon = None
        self._population = None
        self._transit_users = None
        self._rasters = []

    def set_clipped_polygon(self, polygon):
        self._clipped_polygon = polygon

    def get_clipped_polygon(self):
        if self._clipped_polygon:
            return self._clipped_polygon
        return self.get_polygon()

    def _rasters_from_shapefile(self, file_name):
        result = []

        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        for i, record in enumerate(records):
            fid = record[0]
            da_id = record[1]
            raster_id = record[2]
            score = record[3] # These rasters dont nhave/need a score from shapefile

            shape = shapes[i]

            polygon = Polygon()
            for index in xrange(len(shape.points)-1):
                item = shape.points[index]
                polygon.add_point(Point(item[0], item[1]))

            raster = Raster(da_id, raster_id, polygon)
            result.append(raster)

        print "Read %d rasters from file: %s" % (len(records), file_name)
        return result

    def get_rasters(self, size):
        if not self._rasters:

            shape_file = RASTER_SHAPEFILE_TEMPLATE % (size, self.get_id())

            if os.path.exists(shape_file):
                self._rasters = self._rasters_from_shapefile(shape_file)
            else:
                raise ValueError("must run make_rasters!!!")
                # index = 1000
                #
                # # Use clipped polygon for rasters... should make things a little faster
                # polygon = self.get_clipped_polygon()
                # raster_points = polygon.get_raster_points(size)
                #
                # for point in raster_points:
                #     p = point.get_square_buffer(size)
                #     intersecting_polygons = p.intersect(polygon)
                #     for clipped in intersecting_polygons:
                #         raster = Raster(self.get_id(), index, clipped)
                #         index += 1
                #         self._rasters.append(raster)
                #
                # writer = ShapeFileWriter()
                # for raster in self._rasters:
                #     writer.add_raster(raster)
                #
                # writer.write(shape_file)
        print "DA: %d rasters: %d" % (self.get_id(), len(self._rasters))
        return self._rasters

    def get_area(self):
        return self._polygon.get_area()

    def get_id(self):
        return self._da_id

    def add_point(self, index, point):
        self._point_dict[index] = point

    def set_population(self, population):
        self._population = population

    def set_transit_users(self, transit_users):
        self._transit_users = transit_users

    def get_population(self):
        return self._population

    def get_transit_users(self):
        return self._transit_users

    def get_percent_transit_users(self):
        return 100.0 * (float(self.get_transit_users())/float(self.get_population()))

    def get_centriod(self):
        raise ValueError("fixman")

    def get_polygon(self):

        if self._polygon is None:
            polygon = Polygon()

            point_index = 0
            while True:
                point = self._point_dict.get(point_index)
                if point is None: break
                polygon.add_point(point)
                point_index += 1

            self._polygon = polygon

        return self._polygon

class DaData(object):

    def __init__(self):

        self._da_dict = {}

        # self._data = {}
        # self._polygons = {}

        self.load_file("data/DA_polygon_points.csv")
        self.load_file_centroids("data/DA_centroids.csv")
        self.load_file_transit_data("data/2016_da_transit.csv")

        # This data can be used to clip DA polygons to get a much more realistic
        # approximation of the populated areas
        self._clip_points = {
            # This is the westside DA... e.g. near blairmore walmart
            47110581 : [
                (52.119256, -106.765271),
                (52.141280, -106.765271),
                (52.141280, -106.751404),
                (52.119256, -106.751404)
            ],
            47110694 : [
                (52.115015, -106.745332),
                (52.104551, -106.745332),
                (52.104551, -106.715892),
                (52.115015, -106.715892)
            ],
            47110540 : [
                (52.115085, -106.699720),
                (52.106229, -106.699720),
                (52.106229, -106.680867),
                (52.115085, -106.680867),
            ],
            47110699 : [
                (52.096483, -106.662102),
                (52.070744, -106.662102),
                (52.070744, -106.645623),
                (52.096483, -106.645623)
            ],
            47110524 : [
                (52.107555, -106.579190),
                (52.083615, -106.579190),
                (52.083615, -106.543656),
                (52.107555, -106.543656)
            ],
            47110689 : [
                (52.140231, -106.561423),
                (52.120732, -106.561423),
                (52.120732, -106.539879),
                (52.140231, -106.539879)
            ],
            47110664 : [
                (52.174050, -106.585627),
                (52.157045, -106.585627),
                (52.157045, -106.548548),
                (52.174050, -106.548548)
            ],
            # North Industrial Area
            47110691 : [
                (52.180000, -106.691798),
                (52.140824, -106.691798),
                (52.140824, -106.620598),
                (52.180000, -106.620598)
            ],
            # Airport
            47110397 : [
                (52.169926, -106.691456),
                (52.156342, -106.691456),
                (52.156342, -106.666565),
                (52.169926, -106.666565)
            ],
            # Lakeview
            47110147 : [
                (52.096588, -106.605754),
                (52.088705, -106.605754),
                (52.088705, -106.586013),
                (52.096588, -106.586013)
            ]
        }
        self._clipping_polygons = {}
        self._clipped_polygons = {}
        self._make_clipping_polygons()
        self._clip()

        self._use_clipped_area()

        self._lat_saskatoon_min =   52.065626
        self._lat_saskatoon_max =   52.212493
        self._lng_saskatoon_min = -106.777544
        self._lng_saskatoon_max = -106.526575

        # self._lat_saskatoon_min = 52.067740
        # self._lat_saskatoon_max = 52.206957
        # self._lng_saskatoon_min = -106.787424
        # self._lng_saskatoon_max = -106.519849

        self._increments = {
            100 : {'lat' : .00089893575680, 'lng' :  .00146049608306}
        }

        self._all_rasters = None

    def get_saskatoon_bounding_box(self):

        bb = Polygon()
        bb.add_point(Point(self._lat_saskatoon_min, self._lng_saskatoon_min))
        bb.add_point(Point(self._lat_saskatoon_min, self._lng_saskatoon_max))
        bb.add_point(Point(self._lat_saskatoon_max, self._lng_saskatoon_max))
        bb.add_point(Point(self._lat_saskatoon_max, self._lng_saskatoon_min))
        return bb

    def get_all_rasters(self, stops):

        increments = self._increments.get(100)
        lat_inc = increments.get('lat')
        lng_inc = increments.get('lng')

        raster_count = 0

        if self._all_rasters is None:
            self._all_rasters = []

            for lat_index in xrange(10000):
                lat = self._lat_saskatoon_min + lat_index * lat_inc
                if lat > self._lat_saskatoon_max:
                    break

                for lng_index in xrange(10000):
                    lng = self._lng_saskatoon_min + lng_index * lng_inc
                    if lng > self._lng_saskatoon_max:
                        break

                    print raster_count, "MAKE RASTER FOR", lat, lng

                    p = Polygon()
                    p.add_point(Point(lat,           lng))
                    p.add_point(Point(lat,           lng + lng_inc))
                    p.add_point(Point(lat + lat_inc, lng + lng_inc))
                    p.add_point(Point(lat + lat_inc, lng))

                    centroid = p.get_centroid()
                    for stop in stops:
                        distance_to_stop = centroid.get_distance(stop.get_point())
                        # print distance_to_stop
                        if distance_to_stop < 1000:
                            self._all_rasters.append(Raster(None, None, p))
                            raster_count += 1
                            break

        return self._all_rasters

    def make_rasters(self, stops):

        all_rasters = self.get_all_rasters(stops)

        das = self.get_das()

        # This is extremely brute force.  It could probably be sped up
        # considerably by only generating potential raster boxes within
        # the bounding box of the DA polygon

        for da_index, da in enumerate(das):
            print "Processing DA: %s: %d" % (da_index, da.get_id())
            index = 1000
            writer = ShapeFileWriter()
            shapefile_name = RASTER_SHAPEFILE_TEMPLATE % ("100", da.get_id())

            p = da.get_polygon()
            for raster in all_rasters:
                intersecting_polygons = p.intersect(raster.get_polygon())

                for clipped in intersecting_polygons:
                    writer.add_raster(Raster(da.get_id(), index, clipped))
                    index += 1

            writer.write(shapefile_name)

    def _use_clipped_area(self):
        for da_id, p in self._clipped_polygons.iteritems():

            da = self.get_da(da_id)
            da_p = da.get_polygon()

            old_area = da_p.get_area()
            da_p.set_area(p.get_area())
            new_area = da_p.get_area()

            da.set_clipped_polygon(p)

            f = 100.0 * new_area/old_area
            print "DaData: Clipping DA %d area %.2f ---> %.2f ( %.2f%% )" % (da_id, old_area, new_area, f)

    def _clip(self):

        for da_id, clipping_p in self._clipping_polygons.iteritems():

#            da_p = self.get_polygon(da_id)

            da = self.get_da(da_id)
            da_p = da.get_polygon()

            intersection = da_p.intersect(clipping_p)
            if len(intersection) != 1:
                raise ValueError('fixme!!')
            self._clipped_polygons[da_id] = intersection[0]

    def _make_clipping_polygons(self):

        for da_id, points in self._clip_points.iteritems():
            p = Polygon()
            for point in points:
                p.add_point(Point(point[0], point[1]))
            self._clipping_polygons[da_id] = p

    def get_clipping_polygons(self):

        result = []
        for da_id, p in self._clipping_polygons.iteritems():
            result.append(p)
        return result

    def get_clipped_polygons(self):

        result = []
        for da_id, p in self._clipped_polygons.iteritems():
            result.append(p)
        return result

    def load_file(self, file_name):

        f = open(file_name, "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue
            # print line.strip()

            parts=line.split(",")
            da_id = int(parts[0].strip())
            point_index = int(parts[1].strip())
            lat = float(parts[2].strip())
            lng = float(parts[3].strip())

            # print da_id, point_index, lat, lng

            point = Point(lat, lng)

            da = self._da_dict.get(da_id)
            if da is None:
                da = DA(da_id)

            da.add_point(point_index, point)
            self._da_dict[da_id] = da

        f.close()
        print "DaData: loaded %d points from %s" % (count, file_name)

    def get_das(self):
        return [da for da in self._da_dict.itervalues()]

    def get_da(self, da_id):
        return self._da_dict.get(da_id)

    def load_file_transit_data(self, file_name):

        f = open(file_name, "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue

            parts=line.split(",")
            # print parts

            da_id =int(parts[1].strip())
            transit_riders = int(parts[2].strip())
            pop = int(parts[3].strip())

            print da_id, transit_riders, pop

            da = self.get_da(da_id)
            if da is None:
                raise ValueError("cant find DA: %d" % da_id)

            if da.get_population() != pop:
                raise ValueError("pop mismatch")

            da.set_transit_users(4 * transit_riders)

        f.close()

        # das = self.get_das()
        # if (count - 1)  != len(das):
        #     raise ValueError("size mismatch: count: %d DAs: %d" % (count, len(das)))


    def load_file_centroids(self, file_name):

        f = open(file_name, "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue

            parts=line.split(",")
            da_id = int(parts[1].strip())
            lat = float(parts[2].strip())
            lng = float(parts[3].strip())
            pop = int(parts[4].strip())

            centroid = Point(lat, lng)

            da = self.get_da(da_id)
            da.set_population(pop)

            # data = self._data.get(da_id, {})

            # data['centroid'] = centroid
            # data['pop'] = pop
            # self._data[da_id] = data

        f.close()

        print "DaData loaded %d centroids from %s" % (count, file_name)

    def get_transit_percentages(self):

        result = []
        das = self.get_das()
        for da in das:
            percent = da.get_percent_transit_users()
            da_id = da.get_id()
            result.append((da_id, percent))

        result = sorted(result)
        return result

    def plot_percent_transit_users(self, file_name):
        from plotter import Plotter

        plotter = Plotter()

        min_percentage = None
        max_percentage = None

        percentages = self.get_transit_percentages()

        for item in percentages:
            percent = item[1]

            if max_percentage is None or percent > max_percentage:
                max_percentage = percent

            if min_percentage is None or percent < min_percentage:
                min_percentage = percent

        for item in percentages:
            percent = item[1]
            da_id = item[0]

            print da_id, percent

def test1():

    daman = DaData()
    daman.plot_percent_transit_users("temp/maps/transit_users_da.html")


if __name__ == "__main__":

    test1()
