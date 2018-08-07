from geometry import Polygon
from geometry import Point

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import POLYGON
from map_html import POLYLINE
from map_html import MARKER
from map_html import CIRCLE_RED_20
from map_html import CIRCLE_RED_5


class Plotter(object):

    def __init__(self):

        self._polygon_list = []
        self._marker_list = []
        self._dot_list = []
        self._polyline_list = []

    def add_dot(self, point):
        self._dot_list.append(point)

    def add_marker(self, point, title, label):
        self._marker_list.append((point, title, label))

    def add_polyline(self, polyline):
        self._polyline_list.append(polyline)

    def add_polygon(self, items):

        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not isinstance(item, Polygon):
                raise ValueError("not a Polygon")
            #print "ADD item", item
            self._polygon_list.append(item)

    def plot(self, file_name):
        print "plot called", file_name

        f = open(file_name, "w")
        f.write(MAP_TOP)

        if len(self._polyline_list):
            for item in self._polyline_list:
                f.write("var polyline = [\n")
                points = item.get_points()
                for point in points:
                    f.write("{lat: %f, lng: %f},\n" % point.get_lat_lng())
                f.write("];\n")

                stroke_color = item.get_attribute("strokeColor", default="#202020")
                stroke_opacity = item.get_attribute("strokeOpacity", default=0.5)
                stroke_weight = item.get_attribute("strokeWeight", default=1)

                f.write(POLYLINE % (stroke_color, stroke_opacity, stroke_weight))

        if len(self._polygon_list):
            for item in self._polygon_list:
                f.write("var polypoints = [\n")
                points = item.get_points()

                for point in points:
                    f.write("{lat: %f, lng: %f},\n" % point.get_lat_lng())
                f.write("];\n")

                # fill_opacity = float(random.randint(0, 1000)/1000.0)

                stroke_color = item.get_attribute("strokeColor", default="#202020")
                stroke_opacity = item.get_attribute("strokeOpacity", default=0.5)
                stroke_weight = item.get_attribute("strokeWeight", default=1)
                fill_color = item.get_attribute("fillColor", default="#ff0000")
                fill_opacity = item.get_attribute("fillOpacity", default=0.1)

                f.write(POLYGON % (stroke_color, stroke_opacity, stroke_weight, fill_color, fill_opacity))

        if len(self._marker_list) > 0:

            f.write("var marker = {\n")
            i = 0
            for item in self._marker_list:
                point = item[0]
                title = item[1]
                label = item[2]
                lat = point.get_lat()
                lng = point.get_lng()
                f.write("%d:{center:{lat:%f,lng:%f},title:'%s',label:'%s',},\n" % (i, lat, lng, title, label))
                i += 1

            f.write("};\n")
            f.write(MARKER)

        if len(self._dot_list) > 0:

            f.write("var circle = {\n")
            i = 0
            for item in self._dot_list:
                point = item
                lat = point.get_lat()
                lng = point.get_lng()
                f.write("%d: {center:{lat: %f, lng: %f},},\n" % (i, lat, lng))
                i += 1

            f.write("};\n")
            f.write(CIRCLE_RED_5)



        f.write(MAP_BOTTOM)
        f.close()
        print "Wrote MAP file: %s" %file_name
