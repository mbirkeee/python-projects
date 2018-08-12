from geometry import Point
from geometry import Polygon

class DA(object):

    def __init__(self, da_id):
        self._da_id = da_id
        self._point_dict = {}
        self._polygon = None
        self._population = None

    def get_id(self):
        return self._da_id

    def add_point(self, index, point):
        self._point_dict[index] = point

    def set_population(self, population):
        self._population = population

    def get_population(self):
        return self._population

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

    def _use_clipped_area(self):
        for da_id, p in self._clipped_polygons.iteritems():

            da = self.get_da(da_id)
            da_p = da.get_polygon()

            # da_p = self.get_polygon(da_id)
            old_area = da_p.get_area()
            da_p.set_area(p.get_area())
            new_area = da_p.get_area()
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

            # data = self._data.get(da_id, {})

            da = self._da_dict.get(da_id)
            if da is None:
                da = DA(da_id)

            da.add_point(point_index, point)
            self._da_dict[da_id] = da

            # data[point_index] = point
            # self._data[da_id] = data

        f.close()
        print "DaData: loaded %d points from %s" % (count, file_name)

    # def get_area(self, da_id):
    #     polygon = self.get_polygon(da_id)
    #     return polygon.get_area()

    # def get_da_id_list(self):
    #     result = [k for k in self._data.iterkeys()]
    #     return result


    def get_das(self):
        return [da for da in self._da_dict.itervalues()]

#    def get_polygons(self):
#        return [da.get_polygon() for da in self._da_dict.itervalues()]

        # result = {}
        # for da_id in self._data.iterkeys():
        #     result[da_id] = self.get_polygon(da_id)
        # return result

    # def get_polygon(self, da_id):
    #
    #     polygon = self._polygons.get(da_id)
    #
    #     if polygon is None:
    #         points_dict = self._data.get(da_id)
    #         polygon = Polygon()
    #
    #         point_index = 0
    #         while True:
    #             point = points_dict.get(point_index)
    #             if point is None: break
    #             polygon.add_point(point)
    #             point_index += 1
    #         self._polygons[da_id] = polygon
    #
    #     return polygon

    # def get_population(self, da_id):
    #     data = self._data.get(da_id)
    #     return data.get('pop')

    def get_da(self, da_id):
        return self._da_dict.get(da_id)

    # def get_centroid(self, da_id):
    #     polygon = self._polygons.get(da_id)
    #     return polygon.get_centroid()
    #
    #     # data = self._data.get(da_id)
    #     # if data is None:
    #     #     raise ValueError("No data for da_id: %s" % repr(da_id))
    #     # return data.get('centroid')

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
