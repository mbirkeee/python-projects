import pyproj
import random

from my_utils import PlotPolygons
from my_utils import Polygon
from my_utils import Point
from my_utils import DaData
from my_utils import DaHeatmap

PROJ = pyproj.Proj("+init=EPSG:32613")


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

    def test_plot_random(self):

        print "test plot called"

        plotter = PlotPolygons()

        for _ in xrange(10):
            p = self.make_test_polygon()
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

        plotter.plot("temp/maps/test_da_polygons.html")

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
#    runner.test_plot_random()
#    runner.test_plot_das()
    runner.test_plot_da_pop_dens()



