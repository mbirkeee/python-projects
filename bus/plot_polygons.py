import pyproj
import random
import math
import ogr

from my_utils import PlotPolygons
from my_utils import Polygon
from my_utils import Point
from my_utils import DaData
from my_utils import DaHeatmap

PROJ = pyproj.Proj("+init=EPSG:32613")

print "import finished"

class Runner(object):

    def __init__(self):
        pass

    def make_test_polygon(self):
        """
        This test method makes a randomly placed diamond shaped polygon
        """

        center_lat = 52.125
        center_lng = -106.650

        center_x, center_y = PROJ(center_lng, center_lat)

        random_offset_x = random.randint(-2000, 2000)
        random_offset_y = random.randint(-2000, 2000)

        center_x += random_offset_x
        center_y += random_offset_y

        size = 100
        poly_points = [
            (-size, 0),
            (0, size),
            (size, 0),
            (0, -size),
            (-size, 0),
        ]

        p = Polygon()

        for item in poly_points:
            x = center_x + item[0]
            y = center_y + item[1]

            print "test polygon point", x, y
            p.add_point(Point(x, y))

        return p


    def make_test_poly_2(self):

        center_lat = 52.125
        center_lng = -106.650

        p = Polygon()

        center_x, center_y = PROJ(center_lng, center_lat)

        center_x += random.randint(-1000, 1000)
        center_y += random.randint(-1000, 1000)

        start_angle = random.randint(0, 20)

        count = 0
        for a in xrange(360/20):
            r = math.radians(start_angle + a*20)

            if count % 2:
                z = 1000
            else:
                z = 400

            x = z * math.cos(r)
            y = z * math.sin(r)

            x = x + center_x
            y = y + center_y

            count += 1

            p.add_point(Point(x, y))

        p.add_attribute('fill_opacity', 0.1)

        return p

    def test_plot_random(self):

        print "test plot called"

        plotter = PlotPolygons()

        poly = []
        for i in xrange(2):
            # p = self.make_test_polygon()
            p = self.make_test_poly_2()
            plotter.add_polygon(p)

            poly.append(p.get_org_poly())

        intersection = poly[0].Intersection(poly[1])
        print repr(intersection)


        if intersection is not None:
            print type(intersection)
            print intersection.ExportToWkt()

            for i in range(0, intersection.GetGeometryCount()):
                g = intersection.GetGeometryRef(i)
                print "%i). %s" %(i, g.ExportToWkt())

                print type(g)
                print dir(g)

                print g.GetGeometryName()
                feature_count = g.GetGeometryCount()
                print "feature_count", feature_count
                if feature_count == 1:
                    gg = g.GetGeometryRef(0)
                    point_count = gg.GetPointCount()
                    if point_count > 0:
                        p = Polygon()
                        for j in xrange(point_count):
                            # GetPoint returns a tuple not a Geometry
                            pt = gg.GetPoint(j)
                            print "%i). POINT (%d %d)" %(j, pt[0], pt[1])
                            p.add_point(Point(pt[0], pt[1]))

                        p.add_attribute("fill_opacity", 1.0)
                        plotter.add_polygon(p)

        plotter.plot("temp/maps/test_polygon.html")

    def test_plot_das(self):

        das = DaData()
        plotter = PlotPolygons()

        da_id_list = das.get_da_id_list()

        for da_id in da_id_list:
            print da_id
            polygon = das.get_polygon(da_id)
            polygon.add_attribute("fill_opacity", 0.1)

            plotter.add_polygon(polygon)

            pop = das.get_population(da_id)
            centroid = das.get_centroid(da_id)
            print pop, centroid

            plotter.add_marker(centroid, "%d" % da_id, "%d" % pop)

        plotter.plot("temp/maps/da_polygons_markers.html")

    def test_plot_da_pop_dens(self):

        das = DaData()
        plotter = PlotPolygons()

        da_id_list = das.get_da_id_list()

        max_pop_density = 0.0
        total_area = 0
        total_pop = 0
        for da_id in da_id_list:
            polygon = das.get_polygon(da_id)

            pop = das.get_population(da_id)
            total_pop += pop
            area = polygon.get_area()
            total_area += area
            pop_density = 1000 * 1000 * pop / area
            if pop_density > max_pop_density:
                max_pop_density = pop_density

        for da_id in da_id_list:
            polygon = das.get_polygon(da_id)

            pop = das.get_population(da_id)
            area = polygon.get_area()
            pop_density = 1000 * 1000 * pop / area
            opacity = pop_density / max_pop_density
            print da_id, pop, area, "density", pop_density

            polygon.add_attribute("fill_opacity", opacity)

            plotter.add_polygon(polygon)

            # pop = das.get_population(da_id)
            # centroid = das.get_centroid(da_id)
            # print pop, centroid
            #
            # plotter.add_marker(centroid, "%d" % da_id, "%d" % pop)

        plotter.plot("temp/maps/da_pop_density.html")
        total_area = total_area / (1000.0 * 1000.0)
        print "total_pop", total_pop
        print "total_area", total_area
        print "total_density", total_pop/total_area

    def test_plot_heatmap(self):

        das = DaData()
        plotter = PlotPolygons()
        heatmap = DaHeatmap()
        heatmap.load_file("temp/da_score.csv")

        da_id_list = heatmap.get_da_id_list()

        for da_id in da_id_list:
            print da_id

            score = heatmap.get_score_normalized(da_id)
            polygon = das.get_polygon(da_id)

            polygon.add_attribute("fill_opacity", score)
            plotter.add_polygon(polygon)

        plotter.plot("temp/maps/test_da_heatmap.html")


if __name__ == "__main__":

    runner = Runner()
    runner.test_plot_random()

#    runner.test_plot_das()
#    runner.test_plot_da_pop_dens()



