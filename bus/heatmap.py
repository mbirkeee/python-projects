import copy
import shapefile

from shapefile_writer import ShapeFileWriter
from da_manager import Raster
from da_manager import DaData

from data_manager import DataManager
from intersect import Intersect

from plotter import Plotter
from plotter import ATTR

from score import Score

from geometry import Point
from geometry import Polygon

from constants import KEY

from modes import MODE_DICT
from modes import BUFFER_METHOD
from modes import SCORE_METHOD

class Heatmap(object):

    def __init__(self):

        print "Heatmap object created"
        self._raster_list = []
        self._load_file_name = None

        # Used for performing subtraction etc.
        self._raster_dict = {}

        self._mode = None
        self._dataset = None
        self._base_path = None
        self._data_man = None
        self._da_man = None
        self._run_flag = False
        self._mode_dict = MODE_DICT
        self._max_score = None
        self._min_score = None
        self._ave_score = None
        self._route_ids = []

        # self._dataset_to_base_map = {
        #     DATASET.JUNE        : BASE.JUNE,
        #     DATASET.JULY        : BASE.JULY,
        #     DATASET.BRT_ORIG    : BASE.BRT
        # }

        self.validate_mode_dict()

    def add_route_id(self, route_id):

        self._route_ids.append(route_id)
        self._route_ids = list(set(self._route_ids))


    def validate_mode_dict(self):
        print "Must validate mode dict"

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

        if not self._mode_dict.has_key(mode):
            print "Invalid mode. Supported modes are:"
            for mode, data in self._mode_dict.iteritems():
                print "  %d: %s" % (mode, repr(data))

        self._mode = mode

    def set_dataset(self, dataset):
        self._dataset = dataset

    def get_buffer_method(self):
        mode_data = self._mode_dict.get(self._mode)
        return mode_data.get(KEY.BUFFER_METHOD)

    def get_score_method(self):
        mode_data = self._mode_dict.get(self._mode)
        return mode_data.get(KEY.SCORE_METHOD)

    def run(self):

        if self._run_flag:
            print "Heatmap already generated, cannot run again"
            return

        self._run_flag = True
        self._data_man = DataManager(self._dataset)
        self._da_man = DaData()
        das = self._da_man.get_das()

        if not self._route_ids:
            stops = self._data_man.get_active_stops()
        else:
            stops = []
            for route_id in self._route_ids:
                route = self._data_man.get_route(route_id)
                route_stops = route.get_stops()
                stops.extend(route_stops)

        buffer_method = self.get_buffer_method()
        if buffer_method is None:
            raise ValueError("Cannot determine buffer method for mode: %d" % self._mode)

        for stop in stops:
            if buffer_method == BUFFER_METHOD.CIRCLE_400:
                stop.make_round_buffer(400)
            elif buffer_method == BUFFER_METHOD.SQUARE_709:
                stop.make_square_buffer(709)
            elif buffer_method == BUFFER_METHOD.DIAMOND_500:
                stop.make_diamond_buffer(500)
            else:
                raise ValueError("mode %d buffer %s not supported" % (self._mode, buffer_method))

        intersect = Intersect()

        try:
            intersect.load(buffer_method, self._dataset)

        except Exception as err:
            print "Intersect().load() Exception: %s" % repr(err)
            if not self._route_ids:
                intersect.process(stops, das)
                intersect.to_shapefile(buffer_method, self._dataset)
            else:
                print "CANNOT compute intersections with subset of stops"
                print "quitting"
                return

        judge = Score(self._data_man)

        score_method = self.get_score_method()

        for da in das:
            rasters = da.get_rasters(100)
            stop_tuples = intersect.get_intersections(group=2, id=da.get_id())
            print "Got %d stops for da_id: %d" % (len(stop_tuples), da.get_id())

            if self._route_ids:
                stop_tuples = self.filter_stop_tuples(stop_tuples, stops)

            for raster in rasters:
                if score_method == SCORE_METHOD.STOP_COUNT:
                    score = judge.get_score_stop_count(raster, stop_tuples)
                else:
                    raise ValueError("Score method not supported")

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

    def plot(self, file_name=None, plotter=None, include_das=True, max_score=None, min_score=None):

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

        for raster in self._raster_list:

            # print "Raster ID", raster.get_id()
            # print "Raster Parent", raster.get_parent_id()

            p = raster.get_polygon()

            score = raster.get_score()
            if score == 0:
                continue

            if score > 0:
                opacity = score / max_score_abs
                color = "#ff0000"
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

    def to_shapefile(self, file_name):
        """
        Dump this heatmap to a shapefile
        """
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

if __name__ == "__main__":

    # h1 = Heatmap()
    # h1.set_mode(1)
    # h1.set_dataset("brt")
    # h1.run()
    #
    # h2 = Heatmap()
    # h2.set_mode(1)
    # h2.set_dataset("brt1")
    # h2.run()
    # #
    # h3 = h2-h1
    # h3.plot("temp/maps/june_brt_mode_1_diff.html")
    #
    # h1.dump_score_csv()
    # h2.dump_score_csv()
    # h3.dump_score_csv()
    #
    # print "h1 max_score", h1.get_max_score()
    # print "h1 min_score", h1.get_min_score()
    # print "h1 ave_score", h1.get_ave_score()
    #
    # print "h2 max_score", h2.get_max_score()
    # print "h2 min_score", h2.get_min_score()
    # print "h2 ave_score", h2.get_ave_score()
    #
    # print "h3 max_score", h3.get_max_score()
    # print "h3 min_score", h3.get_min_score()
    # print "h3 ave_score", h3.get_ave_score()

    h4 = Heatmap()
    h4.set_dataset("brt1")
    h4.add_route_id(102281938)
    h4.add_route_id(102281939)
    h4.add_route_id(102281940)
    h4.add_route_id(102281941)
    h4.set_mode(1)
    h4.run()
    h4.plot("temp/maps/brt_route_heatmap_mode_1.html")

    # print "h2 max_score", h2.get_max_score()
