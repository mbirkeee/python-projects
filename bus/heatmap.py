import os
import copy
import shapefile
import math
import pprint
import numpy as np
import random

#import matplotlib.pyplot as plt

from shapefile_writer import ShapeFileWriter
from da_manager import Raster
from da_manager import DaData

from data_manager import dataman_factory
from intersect import Intersect

from dataset import DATASET
from dataset import SERVICE

from modes import ModeMan

from plotter import Plotter
from plotter import ATTR

from score import Score
from score import ScoreManager

from geometry import Point
from geometry import Polygon

from modes import BUFFER_METHOD

from make_stop_intersections import BufferManager
from my_utils import get_butterworth_decay

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

        self._intersect = None
        self._buffers_made = None
        self._dataset = None
        self._base_path = None
        self._dataman = None
        self._da_man = None
        self._run_flag = False

        self._mode_man = ModeMan()
        self._max_score = None
        self._min_score = None
        self._ave_score = None
        self._route_ids = []

        if shapefile:
            self.from_shapefile(shapefile)

    def get_model(self):
        return self._mode_man.get_model()

    def print_model(self):
        self._mode_man.print_model()

    def make_random_model(self):
        self._mode_man.make_random_model()

    def set_service_time(self, service_time):
        self._mode_man.set_service_time(service_time)

    def set_service_day(self, service_day):
        self._mode_man.set_service_day(service_day)

    def add_route_id(self, route_id):
        self._route_ids.append(route_id)
        self._route_ids = list(set(self._route_ids))

    def get_max_score(self):
        if self._max_score is None:
            self.process_scores()

        return self._max_score

    def get_min_score(self):
        if self._min_score is None:
            self.process_scores()

        return self._min_score

    def get_ave_score(self):
        if self._ave_score is None:
            self.process_scores()

        return self._ave_score

    def process_scores(self):

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

        print self._min_score
        print self._ave_score
        print self._max_score

    def make_file_name(self, start):
        # print "make name starting with", start

        parts = start.split(".")
        if len(parts) != 2:
            raise ValueError("invalid name template")

        base = parts[0]
        extension = parts[1]
        # print "the extension is ", extension

        parts = base.split("/")
        # print "base parts", parts
        last_part = parts[-1]
        # print "last part >>%s<<" % last_part

        mode = self._mode_man.get_mode()
        time = self._mode_man.get_service_time_str()
        day = self._mode_man.get_service_day_str()

        if len(last_part) > 0:
            last_part += "_"

        last_part += "mode_%d_time_%s_%s_%s.%s" % (mode, time, day, self._dataset, extension)
        # print "last_part", last_part

        result = ['temp']
        result.extend(parts[:-1])
        result.append(last_part)
        # print "result", result

        file_name = "/".join(result)

        # print "file_name_done", file_name
        return file_name

    def to_da_csv(self, file_name=None):

        scores = self.get_da_scores()
        f = open(file_name, "w")

        index = 1
        f.write("fid,da_id,score\n")
        for item in scores:
            f.write("%d,%d,%f\n" % (index, item[0], float(item[1])))
            index += 1

        f.close()

    def to_csv(self, file_name=None):

        x = []
        for raster in self._raster_list:
            centroid = raster.get_centroid()
            # print repr(centroid)
            lat = centroid.get_lat()
            lng = centroid.get_lng()
            x.append((raster.get_score(), raster.get_parent_id(), raster.get_id(), lat, lng))

        x = sorted(x)
        x.reverse()

        if file_name is None:
            file_name = self.make_file_name("csv/heatmaps/heatmap.csv")

        f = open(file_name, "w")
        f.write("index,score,da_id,raster_id,lat,lng\n")
        for i, item in enumerate(x):
            score = item[0]
            da_id = item[1]
            raster_id = item[2]
            lat = item[3]
            lng = item[4]
            f.write("%d,%f,%d,%d,%f,%f\n" % (i, score, da_id, raster_id,lat,lng) )
        f.close()

        print "Wrote %d scores to: %s" % (len(x), file_name)

    def set_mode(self, mode):
        if self._mode_man.get_mode() is not None:
            print "Mode %d cannot be changed" % self._mode_man.get_mode()

        self._mode_man.set_mode(mode)

    def set_dataset(self, dataset):
        self._dataset = dataset

    def make_buffers(self, stops, buffer_method):


        if self._buffers_made is not None and self._buffers_made == buffer_method:
            print "Buffers already made"
            return False
        if buffer_method == BUFFER_METHOD.NONE:
            print "No buffers required"
            return False

        buffer_man = None
        if buffer_method in [BUFFER_METHOD.NETWORK_400]:
            buffer_man = BufferManager(buffer_method, self._dataset)

        print "Making stop buffers for %d stops..." % len(stops)
        for stop in stops:
            stop.make_buffer(buffer_method, buffer_manager=buffer_man)

        print "Stop buffers complete"
        return True

    def run(self, force=False, random_model=False):
        """
        NOTE: This was written to be run only once then hacked to run random models
        """
        if self._run_flag and not random_model:
            print "Heatmap already generated, cannot run again"
            return

        # See if the shapefile already exists
        shapefile_name = None
        if not force:
            shapefile_name = self.make_file_name("shapefiles/heatmaps/heatmap.shp")
            if not os.path.exists(shapefile_name):
                shapefile_name = None

        if shapefile_name:
            self.from_shapefile(shapefile_name)
            return False

        self._run_flag = True

        if self._dataman is None:
            self._dataman = dataman_factory(self._dataset)

        if self._da_man is None:
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

        # print "TEST RETURN" * 5
        # return

        if buffer_method is None:
            raise ValueError("Cannot determine buffer method for mode: %d" % self._mode)

        buffers_made = self.make_buffers(stops, buffer_method)
        if buffers_made:
            # Only need to compute intersections if new buffers were made
            self._intersect = Intersect()

            try:
                self._intersect.load(buffer_method, self._dataset, all_stops)

            except Exception as err:
                print "Intersect().load() Exception: %s" % repr(err)
                if not self._route_ids:
                    self.make_buffers(all_stops, buffer_method)
                    self._intersect.process(all_stops, das)
                    self._intersect.to_shapefile(buffer_method, self._dataset, all_stops)
                else:
                    print "CANNOT compute intersections with subset of stops"
                    print "quitting"
                    return False
        else:
            print "BUFFERS ALREADY MADE!!!!!"

        judge = Score(self._dataman, self._mode_man)
        stop_demand = self._mode_man.get_stop_demand()

        # This loop computes the stop demand if required --------------------------------
        if stop_demand is not None:
            for stop in stops:
                stop.compute_demand(self._intersect, self._da_man, stop_demand)
                # print "Stop: %d DEMAND: %f" % (stop.get_id(), stop.get_demand())

        # End of loop computing stop demand ----------------------------------------------

        self._raster_list = []
        self._raster_dict = {}

        for da in das:
            rasters = da.get_rasters(100)
            stop_tuples = self._intersect.get_intersections(group=2, id=da.get_id())
            print "DA: %d stops: %d" % (da.get_id(), len(stop_tuples))

            if self._route_ids: # Only the scores for a subset of routes are being calculated
                stop_tuples = self.filter_stop_tuples(stop_tuples, stops)

            for raster in rasters:
                score = judge.get_score(raster, stop_tuples)

                if score > 0:
                    raster.set_score(score)
                    self.add_raster(raster)

        return True

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
            print "from_shapefile(): Heatmap already loaded"
            return

        print "from_shapefile(): Loading from shapefile: %s" % file_name
        self._run_flag = True
        self._load_file_name = file_name

        sf = shapefile.Reader(file_name)
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        print "from_shapefile(): Loaded %d records" % len(records)

        # This loop converts the loaded shapefile data itn "rasters"
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

    def get_da_scores(self, clip_level=0.4):
        """
        NOTE: It looks like clipping some of the extreme rasters results is a better correlation
        """
        da_dict = {}

        if self._da_man is None:
            self._da_man = DaData()

        max_score = None

        for raster in self._raster_list:
            score = raster.get_score()
            if max_score is None or score > max_score:
                max_score = score

        clipped_count = 0

        if clip_level is not None:
            max_score = clip_level * max_score

        for raster in self._raster_list:
            # print dir(raster)
            p = raster.get_polygon()
            da_id = raster.get_parent_id()
            score = raster.get_score()

            if score > max_score:
                score = max_score
                clipped_count += 1

            # This is the area of the raster, not the DA! Don't get confused
            area = p.get_area()
            # print da_id, score, area

            da_data = da_dict.get(da_id, {})
            total_score = da_data.get('total_score', 0.0)
            total_score += area * score
            da_data['total_score'] = total_score
            total_area = da_data.get('total_area', 0.0)
            total_area += area
            da_data['total_area'] = total_area
            da_dict[da_id] = da_data

        for da_id, da_data in da_dict.iteritems():
            ave_score = da_data.get('total_score') / da_data.get('total_area')
            da_data['ave_score'] = ave_score

            da = self._da_man.get_da(da_id)
            da.set_score(ave_score)

        # Get a list of all DAs
        das = self._da_man.get_das()

        da_list = []
        for da in das:
            da_id = da.get_id()
            da_data = da_dict.get(da_id)
            if da_data is None:
                # print "NO DATA FOR DA", da_id
                ave_score = 0.0
            else:
                ave_score = da_data.get('ave_score')

            # ave_score = random.randint(0, 10)
            da_list.append((da_id, ave_score))

        da_list = sorted(da_list)

        for item in da_list:
            pass
            # print "DA score item", item

        if clipped_count:
            print "get DA score clipped: %d (cliped max score: %f)" %(clipped_count, max_score)
        return da_list

    def pearson_da(self, other=None):

        from scipy.stats import pearsonr
        from scipy.stats import zscore

        raster_clip = self._mode_man.get_raster_clip()

        print "USING RASTER CLIP", raster_clip
        my_scores = self.get_da_scores(clip_level=raster_clip)

        outliers = [(item[1], item[0]) for item in my_scores]
        outliers = sorted(outliers)

        for item in outliers:
            print item

        outlier_das = outliers[-6:]
        outlier_das = [item[1] for item in outlier_das]

        print "outlier_das"
        print outlier_das

        if other:
            other_scores = other.get_da_scores()
        else:
            if self._da_man is None:
                self._da_man = DaData()
            other_scores = self._da_man.get_transit_percentages()

        # my_sc = []
        # for item in my_scores:
        #     score = item[1]
        #     da_id = item[0]
        #     if da_id in outlier_das:
        #         continue
        #     my_sc.append(score)
        #
        # other_sc = []
        # for item in other_scores:
        #     score = item[1]
        #     da_id = item[0]
        #     if da_id in outlier_das:
        #         continue
        #     other_sc.append(score)


        my_sc = [item[1] for item in my_scores]
        other_sc = [item[1] for item in other_scores]

        result = pearsonr(my_sc, other_sc)
        print result

        print "Get Z scores"

        my_z = zscore(my_sc)
        other_z = zscore(other_sc)

        result = pearsonr(my_z, other_z)
        print result
        return result

    def plot_das(self, file_name, log=False):

        if self._da_man is None:
            self._da_man = DaData()

        # Compute the average score for the DAs
        score_list = self.get_da_scores()
        score_man = ScoreManager(score_list)
        score_man.set_clip_level(0.6, clip_color="#ff0000")

        # Make a plotter object
        plotter = Plotter()
        for item in score_list:
            da_id = item[0]
            da = self._da_man.get_da(da_id)
            p = da.get_polygon()

            opacity, color = score_man.get_score(da_id, opacity=True, log_score=log)

            p.set_attribute(ATTR.FILL_COLOR, color)
            p.set_attribute(ATTR.FILL_OPACITY, opacity)
            p.set_attribute(ATTR.STROKE_WEIGHT, 1)
            p.set_attribute(ATTR.STROKE_COLOR, "#202020")
            p.set_attribute(ATTR.STROKE_OPACITY, 1)
            plotter.add_polygon(p)

        plotter.plot(file_name)

    def plot(self, file_name=None, plotter=None, include_das=True, max_score=None, min_score=None, log=False, sqrt=False, z_score=False):

        heat_color = HeatmapColor()

        if file_name is None:
            file_name = self.make_file_name("maps/heatmap.html")

            # file_name = "temp/maps/heatmap_mode_%s_%s.html" % (self._mode, self._dataset)

        if plotter is None:
            write_file = True
            plotter = Plotter()
        else:
            write_file = False

        # Make a list of scores and pass into score manager
        score_list = [(raster, raster.get_score()) for raster in self._raster_list]
        score_man = ScoreManager(score_list)
        score_man.set_clip_level(0.5, clip_color="#ff0000")

        for raster in self._raster_list:
            p = raster.get_polygon()

            # score = raster.get_score()
            # opacity, color = score_man.get_score(raster, opacity=True, log_score=True)
            opacity, color = score_man.get_score(raster, opacity=True, log_score=log)

            if opacity == 0:
                continue

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

    def to_shapefile_da(self, file_name=None):

        if not self._run_flag:
            raise ValueError("no heatmap data")

        if self._da_man is None:
            self._da_man = DaData()

        self.get_da_scores()

        writer = ShapeFileWriter()
        das = self._da_man.get_das()
        for da in das:
            writer.add_da(da)

        if file_name is None:
            file_name = self.make_file_name("shapefiles/heatmaps/heatmap_DA.shp")

        writer.write_heatmap_da(file_name)

    def to_shapefile(self, file_name=None):
        """
        Dump this heatmap to a shapefile
        """

        if not self._run_flag:
            raise ValueError("no heatmap data")

        if file_name is None:
            file_name = self.make_file_name("shapefiles/heatmaps/heatmap.shp")

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
    h.set_mode(23)
    h.set_dataset(DATASET.JUNE)
    h.run()

    h.to_shapefile()
    h.plot()

def test7():

    h1 = Heatmap()
    h1.set_mode(15)
    h1.set_dataset(DATASET.BRT_1)
    h1.set_service_time("8:00")
    h1.run()
    h1.to_shapefile()
    h1.plot()

    h2 = Heatmap()
    h2.set_mode(15)
    h2.set_dataset(DATASET.BRT_1)
    h2.set_service_time("11:15")
    h2.run()
    h2.to_shapefile()
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


    def plot_histogram(self, bins=25):
        score_min = None
        score_max = None

        fig, ax = plt.subplots(figsize=(10, 6))

        for item in self._heatmaps:
            h = item[0]
            raster_dict = h.get_raster_dict()
            for key, r in raster_dict.iteritems():
                score = r.get_score()
                if score_max is None or score > score_max:
                    score_max = score

                if score_min is None or score < score_min:
                    score_min = score

        bin_size = (score_max - score_min) / bins

        x = np.zeros(bins)
        for i in xrange(bins):
            x[i] = score_min + 0.5 * bin_size + i * bin_size


        print x

        for item in self._heatmaps:
            h = item[0]
            label = item[1]
            y = np.zeros(bins)
            raster_dict = h.get_raster_dict()
            for key, r in raster_dict.iteritems():
                score = r.get_score()

                for i in xrange(bins):
                    if score < ( score_min + (i + 1) * bin_size ):
                        y[i] += 1
                        break

            print y
            line, = ax.plot(x, y, label=label)

        plt.title(self._title)
        plt.ylabel(self._label_y)
        plt.xlabel(self._label_x)

        plt.show()

    def plot(self):

        fig, ax = plt.subplots(figsize=(10, 6))

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
            # line, = ax.loglog(x, y, label=label)
            # line, = ax.plot(x, y, label=label)
            line, = ax.semilogx(x, y, label=label)

        # ax.legend(loc='lower left')
        ax.legend(loc='upper right')

        plt.title(self._title)
        plt.ylabel(self._label_y)
        plt.xlabel(self._label_x)

        plt.show()

def test8():

    h1 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_20_time_8_00_mwf_june.shp")
    h2 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_19_time_8_00_mwf_june.shp")
    h3 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_21_time_8_00_mwf_june.shp")

    h4 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_15_time_8_00_mwf_june.shp")
    h5 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_22_time_8_00_mwf_june.shp")
    h6 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_23_time_8_00_mwf_june.shp")

#    h3 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_17_brt1.shp")
#    h4 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_18_brt1.shp")


    plotter = RasterPlot()

    plotter.add_heatmap(h1, "Diamond Buffer - grid")
    plotter.add_heatmap(h2, "Network Buffer - grid")
    plotter.add_heatmap(h3, "Circle Buffer - grid")

    plotter.add_heatmap(h4, "Circle Buffer - crow")
    plotter.add_heatmap(h5, "Network Buffer - crow")
    plotter.add_heatmap(h6, "Diamond Buffer - crow")

#    plotter.add_heatmap(h3, "dpass = 100")
#    plotter.add_heatmap(h4, "dpass = 400")

    plotter.plot()

    # h3 = (h2 - h1)
    # h3.plot("temp/maps/temp.html")
    # print "max score", h3.get_max_score()
    # print "ave score", h3.get_ave_score()

def test9():

    h1 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_20_time_8_00_mwf_brt.shp")
    h2 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_20_time_8_00_mwf_june.shp")

    h3 = h2-h1

    plotter = RasterPlot()

    plotter.add_heatmap(h3, "Diamond Buffer - grid")
    # plotter.plot()
    plotter.plot_histogram(bins = 100)

def test10():


    h = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_15_time_11_15_mwf_brt1.shp")
    h1 = Heatmap("temp/shapefiles/heatmaps/heatmap_mode_15_time_8_00_mwf_brt1.shp")
    h1.plot_das("temp/maps/plot_da.html")

    x, y = h.pearson_da(other = h1)


def test11():

    h = Heatmap()
    h.set_dataset(DATASET.JUNE)
    h.set_mode(51)
    h.run(force=True)

    # h.to_shapefile()
    # h.to_shapefile_da()

    # h.plot(log=False)
    # h.plot_das("temp/maps/das.html", log=True)

    x, y = h.pearson_da()

def test_random():

    h = Heatmap()
    h.set_dataset(DATASET.JUNE)
    h.set_service_time("8:00")
    h.set_service_day(SERVICE.MWF)


    while True:
        h.make_random_model()
        h.print_model()
        h.run(force=True, random_model=True)
        h.print_model()
        model = h.get_model()
        x, y = h.pearson_da()

        f = open("rand.txt", "a")
        f.write("%s,%s,%s\n" % (repr(x), repr(y), repr(model)))
        f.close()

if __name__ == "__main__":

    test_random()
    # test11()
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
