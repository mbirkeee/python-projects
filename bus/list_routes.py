import argparse
import my_utils
import pyproj

from transit_routes import TransitRoutes

from map_html import TOP as MAP_TOP
from map_html import BOTTOM as MAP_BOTTOM
from map_html import CIRCLE1, CIRCLE2
from heatmap_html import HEATMAP_TOP



from my_utils import base_path_from_date

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        self._route_id = args.route_id
        self._date = args.date
        self._base_path = base_path_from_date(args.date)

        self._routes = TransitRoutes(self._base_path)

    def run(self):

        print self._route_id
        print self._base_path

        result = []
        if self._route_id is None:
            route_ids = self._routes.get_route_ids()
            for route_id in route_ids:
                name = self._routes.get_route_name_from_id(route_id)
                number = self._routes.get_route_number_from_id(route_id)

                result.append((int(number), name, route_id))

            s = sorted(result)
            for item in s:
                print "%5d  %40s (%5d)" % (item[0], item[1], item[2])

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='List routes and stops per route')
    parser.add_argument("--route_id", help="Route ID", type=str)
    parser.add_argument("--date", help="june/july/brt", type=str, required=True)

    args = parser.parse_args()

    runner = Runner(args)
    runner.run()
