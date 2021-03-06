import copy
import shapefile
import math
import pprint

import matplotlib.pyplot as plt

from shapefile_writer import ShapeFileWriter
from da_manager import Raster
from da_manager import DaData

from data_manager import dataman_factory
from intersect import Intersect

from dataset import DATASET
from modes import ModeMan

from plotter import Plotter
from plotter import ATTR

from score import Score

from geometry import Point
from geometry import Polygon

from modes import BUFFER_METHOD


class HeatmapColor(object):
    def __init__(self):

        self._data = self.load_csv_file("CoolWarmUChar257.csv")

    def load_csv_file(self, filename):
        f = open("CoolWarmUChar257.csv")
        line_count = 0

        result = []

        for line in f:
            line_count += 1
            if line_count == 1: continue

            parts = line.split(",")
            scalar = float(parts[0].strip())
            r = int(parts[1].strip())
            g = int(parts[2].strip())
            b = int(parts[3].strip())

            #print "%f %s %s %s" % (scalar, r, g, b)

            result.append((scalar, r, g, b))

        f.close()
        return result

    def get_color(self, value, max_val):

        if value > 0:

            if value > max_val:
                return "#fff240"

            score = float(value)/float(max_val)

            score = 0.5 + score / 2.0

            print "consider score", score

            min_diff = None
            min_item = None

            # This is very brute force...
            for item in self._data:
                diff = abs(item[0] - score)
                if min_diff is None or diff < min_diff:
                    min_diff = diff
                    min_item = item
                    # print "setting min_item", repr(min_item)
            result = "#%02x%02x%02x" % (min_item[1], min_item[2], min_item[3])

            return result

        else:
            raise ValueError("handle negative values")

class Heatmap(object):

    def __init__(self, shapefile=None):

        self._raster_list = []
        self._load_file_name = None

        # Used for performing subtraction etc.
        self._raster_dict = {}

        self._mode = None

        self._dataset = None
        self._base_path = None
        self._dataman = None
        self._da_man = None
        self._run_flag = False

        # self._mode_dict = MODE_DICT
        self._mode_man = ModeMan()
        self._max_score = None
        self._min_score = None
        self._ave_score = None
        self._route_ids = []

        if shapefile:
            self.from_shapefile(shapefile)

    def add_route_id(self, route_id):

        self._route_ids.append(route_id)
        self._route_ids = list(set(self._route_ids))

    def get_max_score(self):
        if self._max_score is None:
            self.get_scores()

        return self._max_score

    def get_min_score(self):
        if self._min_score is None:
            self.get_scores()

        return self._min_score

    def get_ave_score(self):
        if self._ave_score is None:
            self.get_scores()

        return self._ave_score

    def get_scores(self):

        min_score = None
        max_score = None
        ave_score = 0

        for raster in self._raster_list:
            # print raster_id
            score = raster.get_score()

            if max_score is None or score > max_score:
                max_score = score

            if min_score is None or score < min_score:
                min_score = score

            ave_score += score
        ave_score = ave_score / len(self._raster_list)

        self._max_score = max_score
        self._min_score = min_score
        self._ave_score = ave_score

    def dump_score_csv(self, file_name=None):

        x = []
        for raster in self._raster_list:
            x.append((raster.get_score(), raster.get_parent_id(), raster.get_id()))

        x = sorted(x)
        x.reverse()

        if file_name is None:
            file_name = "temp/csv/score_mode_%s_%s.csv" % (self._mode, self._dataset)

        f = open(file_name, "w")
        f.write("index,score,da_id,raster_id\n")
        for i, item in enumerate(x):
            score = item[0]
            da_id = item[1]
            raster_id = item[2]
            f.write("%d,%f,%d,%d\n" % (i, score, da_id, raster_id) )
        f.close()

        print "Wrote %d scores to: %s" % (len(x), file_name)

    def set_mode(self, mode):
        if self._mode is not None:
            print "Mode %d cannot be changed" % self._mode

        mode = int(mode)
        self._mode_man.set_mode(mode)
        self._mode = mode

    def set_dataset(self, dataset):
        self._dataset = dataset

    def make_buffers(self, stops, buffer_method):

        if buffer_method == BUFFER_METHOD.NONE:
            print "No buffers required"
            return

        print "Making stop buffers for %d stops..." % len(stops)
        for stop in stops:
            stop.make_buffer(buffer_method)

        print "Stop buffers complete"

    def run(self):

        if self._run_flag:
            print "Heatmap already generated, cannot run again"
            return

        self._run_flag = True
        self._dataman = dataman_factory(self._dataset)
        self._da_man = DaData()
        das = self._da_man.get_das()

        # Use all stops to check if intersections should be updated
        all_stops = self._dataman.get_stops()

        if not self._route_ids:
            # Only include active stops
            stops = self._dataman.get_active_stops()
        else:
            stops = []
            for route_id in self._route_ids:
                route = self._dataman.get_route(route_id)
                route_stops = route.get_stops()
                stops.extend(route_stops)

        buffer_method = self._mode_man.get_buffer_method()

        if buffer_method is None:
            raise ValueError("Cannot determine buffer method for mode: %d" % self._mode)

        self.make_buffers(stops, buffer_method)
        intersect = Intersect()

        try:
            intersect.load(buffer_method, self._dataset, all_stops)

        except Exception as err:
            print "Intersect().load() Exception: %s" % repr(err)
            if not self._route_ids:
                self.make_buffers(all_stops, buffer_method)
                intersect.process(all_stops, das)
                intersect.to_shapefile(buffer_method, self._dataset, all_stops)
            else:
                print "CANNOT compute intersections with subset of stops"
                print "quitting"
                return

        judge = Score(self._dataman, self._mode)
        judge.set_time_str(self._time_str)

        for da in das:
            rasters = da.get_rasters(100)
            stop_tuples = intersect.get_intersections(group=2, id=da.get_id())
            print "DA: %d stops: %d" % (da.get_id(), len(stop_tuples))

            if self._route_ids: # Only the scores for a subset of routes are being calculated
                stop_tuples = self.filter_stop_tuples(stop_tuples, stops)

            for raster in rasters:
                score = judge.get_score(raster, stop_tuples)

                if score > 0:
                    raster.set_score(score)
                    self.add_raster(raster)

    def filter_stop_tuples(self, stop_tuples, stops):
        result = []
        allowable_stop_ids = [stop.get_id() for stop in stops]
        for stop_tuple in stop_tuples:
            stop_id = stop_tuple[1]
            if not stop_id in allowable_stop_ids:
                continue
            result.append(stop_tuple)
        return result

    def add_raster(self, raster):

        # print "add raster called", repr(raster)
        self._raster_list.append(raster)

    def from_shapefile(self, file_name):
        """
        Load this heatmap from a file
        """

        if self._run_flag:
            print "heatmap already loaded"
            return

        self._run_flag = True

        self._load_file_name = file_name

        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for i, record in enumerate(records):
            # print repr(record)
            fid = record[0]
            da_id = record[1]
            raster_id = record[2]
            score = record[3]

            shape = shapes[i]

            # print "------------------------------------"
            # print repr(shape)
            # print len(shape.points)
            polygon = Polygon()
            for index in xrange(len(shape.points)-1):
                item = shape.points[index]
                # print item
                polygon.add_point(Point(item[0], item[1]))

            raster = Raster(da_id, raster_id, polygon)
            raster.set_score(score)

            self._raster_list.append(raster)

    def plot(self, file_name=None, plotter=None, include_das=True, max_score=None, min_score=None, log=False, sqrt=False):

        heat_color = HeatmapColor()

        if file_name is None:
            file_name = "temp/maps/heatmap_mode_%s_%s.html" % (self._mode, self._dataset)

        if plotter is None:
            write_file = True
            plotter = Plotter()
        else:
            write_file = False

        if max_score is None:
            max_score = -9999999
            for raster in self._raster_list:
                score = raster.get_score()
                if score > max_score:
                    max_score = score

        if min_score is None:
            min_score = 9999999
            for raster in self._raster_list:
                score = raster.get_score()
                if score < min_score:
                    min_score = score

        max_score_abs = max(abs(min_score), abs(max_score))
        max_score_log = math.log10(max_score_abs)
        max_score_sqrt = math.sqrt(max_score_abs)

        for raster in self._raster_list:

            # print "Raster ID", raster.get_id()
            # print "Raster Parent", raster.get_parent_id()

            p = raster.get_polygon()

            score = raster.get_score()
            if score == 0:
                continue

            if score > max_score:
                score = max_score

            if score < min_score:
                score = min_score

            # if sqrt:
            #
            #     color = heat_color.get_color(math.sqrt(score), math.sqrt(max_score))
            #
            # else:
            #     color = heat_color.get_color(score, max_score)
            #
            # opacity = score / max_score


            if score > 0:
                if log:
                    opacity = math.log10(score) / max_score_log
                elif sqrt:
                    opacity = math.sqrt(score) / max_score_sqrt
                else:
                    opacity = score / max_score_abs

                if score >= max_score:
                    color = "#fff240"
                else:
                    color = "#ff0000"
                    # color = "#000000"
            else:
                opacity = -1.0 * score / max_score_abs
                color = "#0000ff"

            p.set_attribute(ATTR.FILL_COLOR, color)
            p.set_attribute(ATTR.FILL_OPACITY, opacity)
            p.set_attribute(ATTR.STROKE_WEIGHT, 0)
            p.set_attribute(ATTR.STROKE_COLOR, "#202020")
            p.set_attribute(ATTR.STROKE_OPACITY, 0)
            plotter.add_polygon(p)

        if include_das:
            if self._da_man is None:
                self._da_man = DaData()
            plotter.add_das(self._da_man.get_das())

        if write_file:
            plotter.plot(file_name)

        print "max_score", max_score_abs
        print "max_score_log", max_score_log
        print "max_score_sqrt", max_score_sqrt


    def to_shapefile(self, file_name=None):
        """
        Dump this heatmap to a shapefile
        """

        if file_name is None:
            file_name = "temp/shapefiles/heatmaps/heatmap_mode_%s_%s.shp" % (self._mode, self._dataset)

        writer = ShapeFileWriter()
        for raster in self._raster_list:
            writer.add_raster(raster)

        writer.write(file_name)

    def get_raster_dict(self):

        if not self._raster_dict:
            dict = {}
            for raster in self._raster_list:

                da_id = raster.get_parent_id()
                raster_id = raster_id = raster.get_id()
                key = "%s-%s" % (da_id, raster_id)

                if dict.has_key(key):
                    raise ValueError("duplicate KEY")

                dict[key] = raster
            self._raster_dict = dict

        return self._raster_dict

    def __div__(self, other):
        print "Dividing heatmaps..."
        result = Heatmap()

        self_dict = self.get_raster_dict()
        other_dict = other.get_raster_dict()

        for key, raster in self_dict.iteritems():
            self_score = raster.get_score()

            if self_score == 0:
                continue

            other_raster = other_dict.get(key)
            if other_raster is None:
                other_score = 0
            else:
                other_score = other_raster.get_score()

            if other_score == 0:
                score = self_score
            else:
                score = self_score / other_score

            result_raster = copy.copy(raster)
            result_raster.set_score(score)
            result.add_raster(result_raster)

        # Unlike the subtract case, don't have to look at "other",
        # because it it basically dividing 0 by "other"

        return result

    def __sub__(self, other):
        """
        Subtract other heatmap from this heatmap
        """

        print "Subtracting heatmaps..."
        result = Heatmap()

        self_dict = self.get_raster_dict()
        other_dict = other.get_raster_dict()

        for key, raster in self_dict.iteritems():
            self_score = raster.get_score()

            other_raster = other_dict.get(key)
            if other_raster is None:
                other_score = 0
            else:
                other_score = other_raster.get_score()

            result_score = self_score - other_score
            result_raster = copy.copy(raster)
            result_raster.set_score(result_score)
            result.add_raster(result_raster)

        # Must also run through other dict in case it has entries not in self dict

        for key, other_raster in other_dict.iteritems():
            self_raster = self_dict.get(key)
            if self_raster is not None:
                continue

            result_score = 0.0 - other_raster.get_score()
            result_raster = copy.copy(other_raster)
            result_raster.set_score(result_score)
            result.add_raster(result_raster)

        return result

def test2():




# x = np.linspace(0, 10, 500)
# dashes = [10, 5, 100, 5]  # 10 points on, 5 off, 100 on, 5 off
#
# fig, ax = plt.subplots()
# line1, = ax.plot(x, np.sin(x), '--', linewidth=2,
#                  label='Dashes set retroactively')
# line1.set_dashes(dashes)
#
# line2, = ax.plot(x, -1 * np.sin(x), dashes=[30, 5, 10, 5],
#                  label='Dashes set proactively')
#
# ax.legend(loc='lower right')
# plt.show()

    import matplotlib.pyplot as plt
    h = Heatmap()
    h.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_9_brt1.shp")

    raster_dict = h.get_raster_dict()
    score_list = []
    for key, r in raster_dict.iteritems():
        print "%d: %f" % (r.get_id(), r.get_score())
        score_list.append(r.get_score())

    y = sorted(score_list)
    y.reverse()

    x = range(len(y))

    h2 = Heatmap()
    h2.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_7_brt1.shp")

    raster_dict = h2.get_raster_dict()
    score_list = []
    for key, r in raster_dict.iteritems():
        print "%d: %f" % (r.get_id(), r.get_score())
        score_list.append(r.get_score())

    y2 = sorted(score_list)
    y2.reverse()

    x2 = range(len(y2))


    fig, ax = plt.subplots()
    # line1, = ax.loglog(x, y, label="July")
    # line2, = ax.loglog(x2, y2, label="BRT 1")

    line1, = ax.semilogy(x, y, label="BRT dpass = 250; Grid")
    line2, = ax.semilogy(x2, y2, label="BRT dpass = 250; Euclidian")

    ax.legend(loc='lower left')
    plt.title("Score vs # of Grid Cells")
    plt.ylabel("Accessibility Score")
    plt.xlabel("Number of 100m X 100m grid Cells")
    plt.show()

def test1():

    july_250 = Heatmap()
    july_250.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_7_july.shp")

    brt_250 = Heatmap()
    brt_250.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_7_brt1.shp")

    july_100 = Heatmap()
    july_100.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_8_july.shp")

    brt_100 = Heatmap()
    brt_100.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_8_brt1.shp")

    diff_250 = brt_250 - july_250
    diff_100 = brt_100 - july_100

    diff_100_250 = diff_100 - diff_250
    diff_100_250.plot("temp/maps/100_200.html")

def test3():

    brt_250_crow = Heatmap()
    brt_250_crow.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_7_brt1.shp")

    brt_250_grid = Heatmap()
    brt_250_grid.from_shapefile("temp/shapefiles/heatmaps/heatmap_mode_9_brt1.shp")

    diff = brt_250_crow - brt_250_grid
    diff.plot("temp/maps/brt_250_grid_crow.html", max_score=5000, sqrt=True)

def test4():
    """
    closets stop heatmap
    """
    h = Heatmap()
    h.set_mode(11)
    h.set_dataset(DATASET.JUNE)
    h.run()
    h.to_shapefile()

    h1 = Heatmap()
    h1.set_mode(11)
    h1.set_dataset(DATASET.JULY)
    h1.run()
    h1.to_shapefile()

    h2 = Heatmap()
    h2.set_mode(11)
    h2.set_dataset(DATASET.BRT_1)
    h2.run()
    h2.to_shapefile()

    # h.plot()

def test5():

    maps = [
        "temp/shapefiles/heatmaps/heatmap_mode_10_june.shp",
        "temp/shapefiles/heatmaps/heatmap_mode_10_july.shp",
        "temp/shapefiles/heatmaps/heatmap_mode_10_brt1.shp",
        "temp/shapefiles/heatmaps/heatmap_mode_11_june.shp",
        "temp/shapefiles/heatmaps/heatmap_mode_11_july.shp",
        "temp/shapefiles/heatmaps/heatmap_mode_11_brt1.shp",
    ]

    for m in maps:
        h = Heatmap()
        h.from_shapefile(m)
        ave = h.get_ave_score()
        print m, ave

def test6():
    h = Heatmap()
    h.set_mode(14)
    h.set_dataset(DATASET.BRT_1)
    h.set_time_str("8:14")
    h.run()

    h.to_shapefile()
    h.plot()

def test7():

    h1 = Heatmap()
    h1.set_mode(15)
    h1.set_dataset(DATASET.BRT_1)
    h1.set_time_str("8:00")
    h1.run()
    h1.to_shapefile("temp/shapefiles/heatmaps/mode_15_8_00.shp")
    h1.plot()

    h2 = Heatmap()
    h2.set_mode(15)
    h2.set_dataset(DATASET.BRT_1)
    h2.set_time_str("11:15")
    h2.run()
    h2.to_shapefile("temp/shapefiles/heatmaps/mode_15_11_15.shp")
    h2.plot()

    h3 = h1 - h2
    h3.plot("temp/maps/diff_test_time_str_BRT1.html")

class RasterPlot(object):

    def __init__(self, title="Accessibility Score vs. Raster Index", label_x="Raster Index", label_y="Accessibility Score"):
        self._title = title
        self._label_x = label_x
        self._label_y = label_y
        self._heatmaps = []

    def add_heatmap(self, heatmap, label):
        self._heatmaps.append((heatmap, label))

    def plot(self):

        fig, ax = plt.subplots()

        for item in self._heatmaps:
            h = item[0]
            label = item[1]

            raster_dict = h.get_raster_dict()
            score_list = []
            for key, r in raster_dict.iteritems():
                print "%d: %f" % (r.get_id(), r.get_score())
                score_list.append(r.get_score())

            y = sorted(score_list)
            y.reverse()
            x = range(len(y))

            # line, = ax.semilogy(x, y, label=label)
            #line, = ax.loglog(x, y, label=label)
            # line, = ax.plot(x, y, label=label)
            line, = ax.semilogx(x, y, label=label)

        ax.legend(loc='lower left')

        plt.title(self._title)
        plt.ylabel(self._label_y)
        plt.xlabel(self._label_x)

        plt.show()

def test8():

    h1 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_15_brt1.shp")
    raise ValueError("temp stop")
    h2 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_16_brt1.shp")
    h3 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_17_brt1.shp")
    h4 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_18_brt1.shp")


    plotter = RasterPlot()
    plotter.add_heatmap(h3, "dpass = 100")
    plotter.add_heatmap(h2, "dpass = 200")
    plotter.add_heatmap(h1, "dpass = 250")
    plotter.add_heatmap(h4, "dpass = 400")

    plotter.plot()

    # h3 = (h2 - h1)
    # h3.plot("temp/maps/temp.html")
    # print "max score", h3.get_max_score()
    # print "ave score", h3.get_ave_score()

if __name__ == "__main__":

    test7()
    raise ValueError("Done")

    mode = 13
    d1 = DATASET.JULY
    d2 = DATASET.BRT_1

    h1 = Heatmap()
    h1.set_mode(mode)
    h1.set_time_str("8:14")
    h1.set_dataset(d1)
    h1.run()
    h1.plot()

    print "h1 max_score", h1.get_max_score()
    print "h1 min_score", h1.get_min_score()
    print "h1 ave_score", h1.get_ave_score()

    h1.dump_score_csv()
    h1.to_shapefile()
    h1.plot()

    # raise ValueError("temp stop")

    h2 = Heatmap()
    h2.set_mode(mode)
    h2.set_dataset(d2)
    h2.set_time_str("8:14")
    h2.run()
    h2.to_shapefile()
    h2.plot()

    h3 = h2 - h1
    h3.plot("temp/maps/diff_%s_%s_mode_%d.html" %(d2, d1, mode))
    #
    # h1.dump_score_csv()
    # h2.dump_score_csv()
    # h3.dump_score_csv()
    # #


    print "h2 max_score", h2.get_max_score()
    print "h2 min_score", h2.get_min_score()
    print "h2 ave_score", h2.get_ave_score()

    print "h3 max_score", h3.get_max_score()
    print "h3 min_score", h3.get_min_score()
    print "h3 ave_score", h3.get_ave_score()

    # h4 = Heatmap()
    # h4.set_dataset("brt1")
    # h4.add_route_id(102281938)
    # h4.add_route_id(102281939)
    # h4.add_route_id(102281940)
    # h4.add_route_id(102281941)
    # h4.set_mode(1)
    # h4.run()
    # h4.plot("temp/maps/brt_route_heatmap_mode_1.html")

    # print "h2 max_score", h2.get_max_score()
