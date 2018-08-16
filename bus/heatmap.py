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

from constants import DATASET
from constants import MODE
from constants import BASE

class Heatmap(object):

    def __init__(self):

        print "Heatmap object instantiated"
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
        self._dataset_to_base_map = {
            DATASET.JUNE        : BASE.JUNE,
            DATASET.JULY        : BASE.JULY,
            DATASET.BRT_ORIG    : BASE.BRT
        }

    def set_mode(self, mode):
        self._mode = mode

    def set_dataset(self, dataset):
        self._dataset = dataset

    def run(self):

        if self._run_flag:
            print "heatmap already generated, cannot run again"
            return

        self._run_flag = True
        self._base_path = self._dataset_to_base_map.get(self._dataset)
        if self._base_path is None:
            raise ValueError("Cannot determine base path from %s" % self._dataset)

        self._data_man = DataManager(self._base_path)
        self._da_man = DaData()
        das = self._da_man.get_das()
        stops = self._data_man.get_stops()

        for stop in stops:
            if self._mode == MODE.ONE:
                stop.make_round_buffer(400)
            else:
                raise ValueError("mode not supported")

        intersect = Intersect()
        try:
            intersect.load(self._mode, self._dataset)
        except Exception as err:
            print "Exception: %s" % repr(err)
            intersect.process(stops, das)
            intersect.to_shapefile(self._mode, self._dataset)

        judge = Score(self._data_man)


        for da in das:
            rasters = da.get_rasters(100)
            stop_tuples = intersect.get_intersections(group=2, id=da.get_id())
            print "Got %d stops for da_id: %d" % (len(stop_tuples), da.get_id())

            for raster in rasters:
                if self._mode == MODE.ONE:
                    score = judge.get_score_stop_count(raster, stop_tuples)
                else:
                    raise ValueError("not supported")

                if score > 0:
                    raster.set_score(score)
                    self.add_raster(raster)

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
