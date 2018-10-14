import random

from heatmap import Heatmap
from heatmap import RasterPlot
from modes import ModeMan
from dataset import DATASET

modes = [
    (24, "1 Minute"),
    (20, "3 Minutes"),
    (25, "5 Minutes"),
    (26, "10 Minutes"),
]

mode_mgr = ModeMan()
mode_mgr.mode_list_summary([item[0] for item in modes])

raise ValueError("temp stop")

heatmaps = []

for item in modes:
    mode = item[0]
    desc = item[1]

    h = Heatmap()
    h.set_mode(mode)
    h.set_dataset(DATASET.BRT)
    if h.run():
        h.to_shapefile()

    heatmaps.append((h, desc))

plotter = RasterPlot()

for item in heatmaps:
    h = item[0]
    desc = item[1]
    plotter.add_heatmap(h, desc)

plotter.plot()

item_10 = heatmaps[3]
h_10 = item_10[0]
item_1 = heatmaps[0]
h_1 = item_1[0]

diff = h_10 - h_1
diff.plot("temp/maps/10_min_1_min.html")

rasters_dist_10 = h_10.get_raster_dict()
rasters_dist_1 = h_1.get_raster_dict()

h_10.plot("temp/maps/wait_10.html")
h_1.plot("temp/maps/wait_1.html")

for key, raster in rasters_dist_10.iteritems():
    score = raster.get_score()

    raster1 = rasters_dist_1.get(key)
    score1 = raster1.get_score()

    if score > 0:
        diff =  100.0 * (score - score1 )/score
        raster.set_score(diff)

h_10.process_scores()

h_10.plot("temp/maps/change_10_1.html", max_score=50)


