import copy
import shapefile
import math

from shapefile_writer import ShapeFileWriter
from da_manager import Raster
from da_manager import DaData

from data_manager import dataman_factory
from intersect import Intersect

from dataset import SERVICE

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
        self._service = None
        self._time_str = None

        self._dataset = None
        self._base_path = None
        self._dataman = None
        self._da_man = None
        self._run_flag = False
        self._mode_dict = MODE_DICT
        self._max_score = None
        self._min_score = None
        self._ave_score = None
        self._route_ids = []

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


    def set_service(self, service):
        self._service = service

    def set_time_str(self, time_str):
        self._time_str = time_str

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

    def make_buffers(self, stops, buffer_method):

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

        buffer_method = self.get_buffer_method()
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

        judge = Score(self._dataman)

        score_method = self.get_score_method()

        for da in das:
            rasters = da.get_rasters(100)
            stop_tuples = intersect.get_intersections(group=2, id=da.get_id())
            print "DA: %d stops: %d" % (da.get_id(), len(stop_tuples))

            if self._route_ids:
                stop_tuples = self.filter_stop_tuples(stop_tuples, stops)

            for raster in rasters:
                if score_method == SCORE_METHOD.STOP_COUNT:
                    score = judge.get_score_stop_count(raster, stop_tuples)
                elif score_method == SCORE_METHOD.DEPARTURES_PER_HOUR:
                    score = judge.get_score_departures_per_hour(raster, stop_tuples, self._service, self._time_str)
                else:
                    raise ValueError("Score method not supported: %s" % score_method)

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

    def plot(self, file_name=None, plotter=None, include_das=True, max_score=None, min_score=None, log=False):

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

            if score > 0:
                if log:
                    opacity = math.log10(score) / max_score_log
                else:
                    opacity = score / max_score_abs

                if score >= max_score:
                    color = "#fff240"
                else:
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

    h1 = Heatmap()
    h1.set_mode(4)
    # h1.set_mode(1)
    h1.set_service(SERVICE.MWF)
    h1.set_time_str("8:14")
    h1.set_dataset("july")
    h1.run()
    h1.plot()

    print "h1 max_score", h1.get_max_score()
    print "h1 min_score", h1.get_min_score()
    print "h1 ave_score", h1.get_ave_score()
    h1.dump_score_csv()
    h1.to_shapefile()

    raise ValueError("temp stop")

    # h2 = Heatmap()
    # h2.set_mode(1)
    # h2.set_dataset("brt1")
    # h2.run()
    # h2.plot("temp/maps/h2.html")
    #
    # #
    # h3 = h2-h1
    # h3.plot("temp/maps/brt1_brt_mode_1_diff.html")
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
