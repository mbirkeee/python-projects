import pyproj
import random
import numpy as np

from my_utils import Plotter
from my_utils import Polygon
from my_utils import Point
from my_utils import DaData
from my_utils import DaHeatmap

PROJ = pyproj.Proj("+init=EPSG:32613")

class Runner(object):

    def __init__(self):
        pass

    def PolyArea(self, x, y):
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

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

    def test_polygon_area(self):

        print "test plot called"
        # das = DaData()

        p = self.make_test_polygon()

        points = [
            (3,4),
            (5,11),
            (12,8),
            (9,5),
            (5,6),
        ]


        x = np.array([item[0] for item in points])
        y = np.array([item[1] for item in points])

        print x
        print y

        area = self.PolyArea(x,y)

        print area

        print p.get_area()

if __name__ == "__main__":

    runner = Runner()
    runner.test_polygon_area()



