import pyproj
import random
import math
import ogr

from my_utils import PlotPolygons
from my_utils import Polygon
from my_utils import Point
from my_utils import DaData
from my_utils import DaHeatmap
from stops import Stops
from intersect import Intersect

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
        """
        Test intersection by plotting random stars
        """
        plotter = PlotPolygons()

        poly = []
        for i in xrange(2):
            # p = self.make_test_polygon()
            p = self.make_test_poly_2()
            plotter.add_polygon(p)
            poly.append(p)

        intersection = poly[0].intersect(poly[1])

        for p in intersection:
            p.add_attribute("fill_opacity", 1.0)
            plotter.add_polygon(p)

        plotter.plot("temp/maps/test_random_intersect.html")

    def test_plot_random2(self):
        """
        Test intersection by plotting random stars
        """
        plotter = PlotPolygons()

        poly = []
        for i in xrange(4):
            # p = self.make_test_polygon()
            p = self.make_test_poly_2()
            plotter.add_polygon(p)
            poly.append(p)

        # intersection = poly[0].intersect(poly[1])

        # for p in intersection:
        #     p.add_attribute("fill_opacity", 1.0)
        #     plotter.add_polygon(p)

        plotter.plot("temp/maps/test_random_2.html")

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


        plotter.plot("temp/maps/da_polygons_with_markers.html")

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

    def test_plot_heatmap(self, file_name_in, file_name_out):

        das = DaData()
        plotter = PlotPolygons()
        heatmap = DaHeatmap()
        heatmap.load_file("temp/%s" % file_name_in)

        da_id_list = heatmap.get_da_id_list()

        for da_id in da_id_list:
            score = heatmap.get_score_normalized(da_id)
            polygon = das.get_polygon(da_id)
            polygon.add_attribute("fill_opacity", score)
            polygon.add_attribute("fill_color", "#00ff00")
            plotter.add_polygon(polygon)

        plotter.plot("temp/maps/%s" % file_name_out)

    def plot_heatmap_change(self):
        das = DaData()
        plotter = PlotPolygons()

        heatmap_june = DaHeatmap()
        heatmap_july = DaHeatmap()

        heatmap_june.load_file("temp/da_score_june.csv")
        heatmap_july.load_file("temp/da_score_july.csv")

        da_id_list = heatmap_june.get_da_id_list()

        for da_id in da_id_list:
            # score_june = heatmap_june.get_score_normalized(da_id)
            # score_july = heatmap_july.get_score_normalized(da_id)

            score_june = heatmap_june.get_score(da_id)
            score_july = heatmap_july.get_score(da_id)

            if score_june == 0:
                change = 0
            else:
                change = 100.0 * (score_july - score_june) / score_june
            print da_id, score_june, score_july, change

            color = None
            if change > 0:
                color = '#0000ff'
            elif change < 0:
                color = '#ff0000'

            if color is not None:
                opacity = abs(change)/100.0

                polygon = das.get_polygon(da_id)
                polygon.add_attribute("fill_opacity", opacity)
                polygon.add_attribute("fill_color", color)
                plotter.add_polygon(polygon)

        plotter.plot("temp/maps/heatmap_change_june_july.html")

    def plot_stop_buffers(self):

        stop = Stops( "../data/sts/csv/2018_05_04/")
        # stop.make_square_buffers(800)
        stop.make_round_buffer(400)

        plotter = PlotPolygons()

        stop_ids = stop.get_ids()
        for stop_id in stop_ids:
            p = stop.get_buffer(stop_id)
            p.add_attribute("fill_opacity", 0.05)
            p.add_attribute("fill_color", "#ff0000")

            plotter.add_polygon(p)

        plotter.plot("temp/maps/stop_buffers.html")

    def plot_stop_da_intersections(self):
        stop = Stops( "../data/sts/csv/2018_05_04/")
        # stop.make_square_buffers(800)
        stop.make_round_buffer(400)
        group1 = {}
        stop_id_list = stop.get_ids()
        for stop_id in stop_id_list:
            group1[stop_id] = stop.get_buffer(stop_id)

        group2 = {}
        das = DaData()
        da_id_list = das.get_da_id_list()
        for da_id in da_id_list:
            group2[da_id] = das.get_polygon(da_id)

        intersect = Intersect()

        intersect.process(group1, group2)

        polygons = intersect.get_intersections_for_group1_id(10004)
        plotter = PlotPolygons()

        for item in polygons:
            p = item[0]
            p.add_attribute("fillOpacity", 0.1)
            p.add_attribute("fillColor", "#ff0000")
            plotter.add_polygon(p)

        for item in polygons:
            p = item[0]
            centroid = p.get_centroid()
            da_id = item[1]
            msg = "da_%d" % da_id
            plotter.add_marker(centroid, msg, "")

        plotter.plot("temp/maps/stop_da_intersect_3004.html")

        polygons = intersect.get_intersections_for_group2_id(47110114)
        plotter = PlotPolygons()

        for item in polygons:
            p = item[0]
            p.add_attribute("fillOpacity", 0.1)
            p.add_attribute("fillColor", "#ff0000")
            plotter.add_polygon(p)

        for item in polygons:
            p = item[0]
            p.add_attribute("fillOpacity", 0.1)
            p.add_attribute("fillColor", "#ff0000")
            p.add_attribute("strokeWeight", 1)
            stop_id = item[1]
            msg = "stop_%d" % stop_id
            centroid = p.get_centroid()
            plotter.add_marker(centroid, msg, "")

        plotter.plot("temp/maps/da_stop_intersect_47110114.html")



if __name__ == "__main__":


    runner = Runner()
#    runner.test_plot_random()
#    runner.test_plot_random2()
#    runner.test_plot_das()
#    runner.test_plot_heatmap('da_score_june.csv', 'heatmap_june.html')
#    runner.test_plot_heatmap('da_score_july.csv', 'heatmap_july.html')

#    runner.plot_heatmap_change()
#    runner.plot_stop_buffers()

    runner.plot_stop_da_intersections()


#    runner.test_plot_da_pop_dens()



