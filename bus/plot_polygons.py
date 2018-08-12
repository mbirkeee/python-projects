import pyproj
import random
import math

from plotter import Plotter

from geometry import Polygon
from geometry import Polyline
from geometry import Polypoint
from geometry import Point

from da_manager import DaData

from my_utils import DaHeatmap
from my_utils import Weight
# from transit_stops import TransitStops
from transit_routes import TransitRoutes

from intersect import Intersect
from score import Score
from constants import BASE

PROJ = pyproj.Proj("+init=EPSG:32613")
DECAY = Weight()

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

        p.set_attribute('fill_opacity', 0.1)

        return p

    def test_plot_random(self):
        """
        Test intersection by plotting random stars
        """
        plotter = Plotter()

        poly = []
        for i in xrange(2):
            # p = self.make_test_polygon()
            p = self.make_test_poly_2()
            plotter.add_polygon(p)
            poly.append(p)

        intersection = poly[0].intersect(poly[1])

        for p in intersection:
            p.set_attribute("fill_opacity", 1.0)
            plotter.add_polygon(p)

        plotter.plot("temp/maps/test_random_intersect.html")

    def test_plot_random2(self):
        """
        Test intersection by plotting random stars
        """
        plotter = Plotter()

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

        plotter = Plotter()

        da_id_list = das.get_da_id_list()

        for da_id in da_id_list:
            polygon = das.get_polygon(da_id)
            polygon.set_attribute("fill_opacity", 0.1)
            plotter.add_polygon(polygon)

            pop = das.get_population(da_id)
            centroid = das.get_centroid(da_id)
            plotter.add_marker(centroid, "%d" % da_id, "%d" % pop)

        clipping = das.get_clipping_polygons()

        for p in clipping:
            p.set_attribute("fillColor", "#0000ff")
            p.set_attribute("fillOpacity", 0.1)
            plotter.add_polygon(p)

        clipped = das.get_clipped_polygons()

        for p in clipped:
            p.set_attribute("fillColor", "#00ff00")
            p.set_attribute("fillOpacity", 0.5)
            plotter.add_polygon(p)
            print "clipped area", p.get_area()

        plotter.plot("temp/maps/da_polygons_with_markers.html")

    def test_plot_da_pop_dens(self):

        das = DaData()
        plotter = Plotter()

        da_id_list = das.get_da_id_list()

        max_pop_density = 0.0
        total_area = 0
        total_pop = 0
        for da_id in da_id_list:
            polygon = das.get_polygon(da_id)
            area = das.get_area(da_id)
            pop = das.get_population(da_id)

            total_pop += pop
            total_area += area
            pop_density = 1000 * 1000 * pop / area
            if pop_density > max_pop_density:
                max_pop_density = pop_density

        for da_id in da_id_list:
            polygon = das.get_polygon(da_id)
            area = das.get_area(da_id)
            pop = das.get_population(da_id)
            pop_density = 1000 * 1000 * pop / area
            opacity = pop_density / max_pop_density
            print da_id, pop, area, "density", pop_density

            polygon.set_attribute("fill_opacity", opacity)

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
        plotter = Plotter()
        heatmap = DaHeatmap()
        heatmap.load_file("temp/%s" % file_name_in)

        da_id_list = heatmap.get_da_id_list()

        for da_id in da_id_list:
            score = heatmap.get_score_normalized(da_id)
            polygon = das.get_polygon(da_id)
            polygon.set_attribute("fill_opacity", score)
            polygon.set_attribute("fill_color", "#00ff00")
            plotter.add_polygon(polygon)

        plotter.plot("temp/maps/%s" % file_name_out)

    def plot_heatmap_change(self):
        das = DaData()
        plotter = Plotter()

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
                polygon.set_attribute("fill_opacity", opacity)
                polygon.set_attribute("fill_color", color)
                plotter.add_polygon(polygon)

        plotter.plot("temp/maps/heatmap_change_june_july.html")

    def plot_stop_buffers(self):

        stop = TransitStops( "../data/sts/csv/2018_05_04/")
        # stop.make_square_buffers(800)
        stop.make_round_buffer(400)

        plotter = Plotter()

        stop_ids = stop.get_ids()
        for stop_id in stop_ids:
            p = stop.get_buffer(stop_id)
            p.set_attribute("fill_opacity", 0.05)
            p.set_attribute("fill_color", "#ff0000")

            plotter.add_polygon(p)

        plotter.plot("temp/maps/stop_buffers.html")

    def plot_test_raster(self):

        das = DaData()

        if True:
            group1 = das.get_polygon_dict()
            da_id_list = das.get_da_id_list()
        else:
            da_id_list = [
                47110049,
                47110045,
                47110046,
            ]

            group1 = {}
            for da_id in da_id_list:
                group1[da_id] = das.get_polygon(da_id)

        # base_path = "../data/sts/csv/2018_05_04/"
        base_path = BASE.JULY
        # base_path = BASE.BRT

        stop_mgr = TransitStops(base_path)

        #------------------------------------------------------------------------------------
        plotter = Plotter()
        polypoint = Polypoint()
        stop_mgr.make_round_buffers(400)
        stops = stop_mgr.get_active_stops()

        for stop in stops:
            polypoint.add_point(stop.get_point())

            # Add buffer
            buffer = stop.get_buffer()
            buffer.set_attribute("fillColor", "#0000ff")
            buffer.set_attribute("fillOpacity", 0.1)
            plotter.add_polygon(buffer)

        polypoint.set_attribute("fillOpacity", 0.8)
        polypoint.set_attribute("radius", 50)
        plotter.add_polypoint(polypoint)
        plotter.plot("temp/maps/stop_locations.html")
        #------------------------------------------------------------------------------------

        raise ValueError("TEMP STOP")

        xx = stop_mgr.get_name(3432)
        print xx
        # raise ValueError("temp stop")

        # stop.make_square_buffers(600)
        stop_mgr.make_round_buffer(400)
        group2 = stop_mgr.get_buffer_polygons()

        intersect = Intersect(group1, group2, limit=2000)

        stop_mgr.compute_demand(intersect, das)
        stop_polygons = intersect.get_intersections(group=1, id=da_id_list[0])

        # -------------------------------------------------------------------------------------
        plotter = Plotter()
        for item in stop_polygons:
            p = item[0]
            p.set_attribute("fillOpacity", 0.1)
            p.set_attribute("fillColor", "#ff0000")
            plotter.add_polygon(p)

        for item in stop_polygons:
            p = item[0]
            centroid = p.get_centroid()
            da_id = item[1]
            msg = "stop_%d" % da_id
            plotter.add_marker(centroid, msg, "")

        da_p = das.get_polygon(da_id_list[0])
        raster_size = 100

        raster_points = da_p.get_raster(raster_size)
        raster_polygons = []
        polypoint = Polyline()
        polypoint.set_attribute("radius", 10)

        for point in raster_points:
            # print "adding raster point", repr(point)
            polypoint.add_point(point)

            p = point.get_square_buffer(raster_size)
            p.set_attribute("fillOpacity", 0.1)
            p.set_attribute("fillColor", "#0000ff")
            p.set_attribute("strokeWeight", 1)
            p.set_attribute("strokeColor", "#202020")
            p.set_attribute("strokeOpacity", 0.1)

            plotter.add_polygon(p)
            raster_polygons.append(p)
        plotter.add_polypoint(polypoint)

        da_p.set_attribute("strokeWeight", 2)
        da_p.set_attribute("strokeColor", "#202020")
        da_p.set_attribute("strokeOpacity", 1)

        plotter.add_polygon(da_p)
        plotter.plot("temp/maps/test_raster_%d.html" % da_id_list[0])

        # ===================================================================
        # Loop through all the raster polygons and compute score
        # This is the number of stop polygons it touches

        judge = Score(base_path, stops=stop_mgr)

        score_list = []
        log_score_list = []

        da_ids = intersect.get_group1_ids()

        # Make a data dict for all DAs in the list
        data = {}
        for da_id in da_ids:
            da_p = das.get_polygon(da_id)
            raster_points = da_p.get_raster(raster_size)
            raster_polygons = []
            for point in raster_points:
                p = point.get_square_buffer(raster_size)
                raster_polygons.append(p)

            stop_polygons = intersect.get_intersections(group=1, id=da_id)

            print "Got %d stop polygons %d raster polygons for DA %d" % \
                  (len(stop_polygons), len(raster_polygons), da_id)
            keep_rasters = []

            for p in raster_polygons:
                # Figure out which stop polygons intersect this raster polygon
                # score = judge.get_score(p, stop_polygons)
                score = judge.get_score_simple(p, stop_polygons)

                if score == 0: continue

                score_list.append(score)
                # if score > 200:
                #     print "CAPPING SCORE"
                #     score = 200

                # score += 1
                try:
                    score_log = math.log10(score)
                    score_log = math.sqrt(score)
                except:
                    score_log = 0

                log_score_list.append(score_log)

                keep_rasters.append((p, score, score_log))

            data[da_id] = {
                'rasters' : keep_rasters,
                'da_p' : da_p
            }

        # Now loop through DAs
        plotter = Plotter()

        score_list = sorted(score_list)
        score_list.reverse()

        log_score_list = sorted(log_score_list)
        log_score_list.reverse()

        # This caps the top score
        max_score = score_list[50]
        max_score_log = log_score_list[10]

        # These are the DAs
        for k, v in data.iteritems():
            da_p = v.get('da_p')
            da_p.set_attribute("fillOpacity", 0)
            da_p.set_attribute("fillColor", "#ffffff")
            da_p.set_attribute("strokeWeight", 2)
            plotter.add_polygon(da_p)

        for k, v in data.iteritems():
            rasters = v.get('rasters')
            da_p = v.get('da_p')
            for item in rasters:
                p = item[0]
                score = item[1]

                if score == 0: continue

                if score > max_score:
                    color = "#ff0000"
                    score = max_score
                else:
                    color = "#0000ff"

                opacity = 0.9 * score / (max_score)

                intersection = p.intersect(da_p)
                for i_p in intersection:
                    i_p.set_attribute("fillOpacity", opacity)
                    i_p.set_attribute("fillColor", color)
                    i_p.set_attribute("strokeWeight", 1)
                    i_p.set_attribute("strokeColor", "#202020")
                    i_p.set_attribute("strokeOpacity", 0.1)
                    plotter.add_polygon(i_p)

        plotter.plot("temp/maps/test_raster_score.html")

        # Now loop through DAs
        plotter = Plotter()

        for k, v in data.iteritems():
            da_p = v.get('da_p')
            da_p.set_attribute("fillOpacity", 0)
            da_p.set_attribute("fillColor", "#ffffff")
            da_p.set_attribute("strokeWeight", 2)
            plotter.add_polygon(da_p)

        for k, v in data.iteritems():
            rasters = v.get('rasters')
            da_p = v.get('da_p')
            for item in rasters:
                p = item[0]
                score = item[2]

                if score == 0: continue

                if score > max_score_log:
                    color = "#ff0000"
                    score = max_score_log
                else:
                    color = "#0000ff"

                opacity = 0.9 * score / (max_score_log)

                intersection = p.intersect(da_p)
                for i_p in intersection:
                    i_p.set_attribute("fillOpacity", opacity)
                    i_p.set_attribute("fillColor", color)
                    i_p.set_attribute("strokeWeight", 1)
                    i_p.set_attribute("strokeColor", "#202020")
                    i_p.set_attribute("strokeOpacity", 0.1)
                    plotter.add_polygon(i_p)

        plotter.plot("temp/maps/test_raster_score_log.html")

        s = sorted(score_list)
        s.reverse()
        f = open("scores.txt", "w")
        for i, score in enumerate(s):
            f.write("%d - %f\n" % (i, score))
        f.close()

    def plot_stop_da_intersections(self):

        dataman = TransitRoutes(BASE.JULY, link_stops=False, link_shapes=False)

        dataman.make_round_buffers(400)
        group1 = dataman.get_stops()

        das = DaData()
        group2 = das.get_das()

        intersect = Intersect(group1, group2)

        s_id = 3312

        polygons = intersect.get_intersections_for_group1_id(s_id)
        plotter = Plotter()

        for item in polygons:
            p = item[0]
            p.set_attribute("fillOpacity", 0.1)
            p.set_attribute("fillColor", "#ff0000")
            plotter.add_polygon(p)

        for item in polygons:
            p = item[0]
            centroid = p.get_centroid()
            da_id = item[1]
            msg = "%d" % da_id
            plotter.add_marker(centroid, msg, msg)

        plotter.plot("temp/maps/stop_da_intersect_%d.html" % s_id )

        polygons = intersect.get_intersections_for_group2_id(47110114)
        plotter = Plotter()

        da = das.get_da(47110114)
        p = da.get_polygon()
        p.set_attribute("fillColor", "#0000ff")
        p.set_attribute("strokeWeight", 2)

        plotter.add_polygon(p)

        for item in polygons:
            p = item[0]
            p.set_attribute("fillOpacity", 0.1)
            p.set_attribute("fillColor", "#ff0000")
            plotter.add_polygon(p)

        for item in polygons:
            p = item[0]
            p.set_attribute("fillOpacity", 0.1)
            p.set_attribute("fillColor", "#ff0000")
            p.set_attribute("strokeWeight", 1)
            stop_id = item[1]
            msg = "stop_%d" % stop_id
            centroid = p.get_centroid()
            plotter.add_marker(centroid, msg, msg)

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

#    runner.plot_test_raster()


#    runner.test_plot_da_pop_dens()



