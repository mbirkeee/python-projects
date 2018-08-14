import shapefile
import argparse
from plotter import Plotter
from geometry import Polygon
from geometry import Point

class Runner(object):
    def __init__(self, args):
        self._file_name = args.file_name

    def run(self):
        print "want to read", self._file_name

        sf = shapefile.Reader(self._file_name)
        records = sf.records()
        shapes = sf.shapes()

        if len(records) != len(shapes):
            raise ValueError("len records != len shapes")

        print "len(records)", len(records)
        print "len(shapes)", len(shapes)

        for record in records:
            # print repr(record)
            fid = record[0]
            da_id = record[1]
            raster_id = record[2]
            score = record[3]

        plotter  = Plotter()

        for i, shape in enumerate(shapes):
            # print "------------------------------------"
            # print repr(shape)
            # print len(shape.points)
            polygon = Polygon()
            for index in xrange(len(shape.points)-1):
                item = shape.points[index]
                # print item
                polygon.add_point(Point(item[0], item[1]))

            plotter.add_polygon(polygon)


        plotter.plot("temp/maps/raster_test_read.html")



if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Raster Heatmap')
   parser.add_argument("-f", "--file_name", help="Shapefile name", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()
