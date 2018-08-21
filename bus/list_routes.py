import argparse

from data_manager import DataManager

class Runner(object):
    """
    This program plots routes/stops
    """
    def __init__(self, args):

        try:
            self._route_id = int(args.route_id)
        except:
            self._route_id = None

        self._route_id = args.route_id
        self._dataset = args.dataset

        self._dataman = None

    def run(self):

        result = []
        if self._route_id is None:

            self._dataman = DataManager(self._dataset, link_stops=False)

            routes = self._dataman.get_routes()
            for route in routes:
                name = route.get_name()
                number = route.get_number()
                route_id = route.get_id()
                result.append((int(number), name, route_id))

            s = sorted(result)
            for item in s:
                print "%5s  %60s %10s" % (repr(item[0]), item[1], repr(item[2]))

                # Format for wiki table
                # print "|| %s || %s || %s || PDF || Map || Notes ||" % (repr(item[0]), item[1], repr(item[2]))

        else:
            self._dataman = DataManager(self._dataset)
            route = self._dataman.get_route(self._route_id)
            stops = route.get_stops()

            print "Stops for Route: %s (%d) %d" % (route.get_name(), route.get_number(), route.get_id())

            for stop in stops:
                print "   STOP: %s (%s)" % (stop.get_name(), stop.get_id())

                routes = stop.get_routes()
                for r in routes:
                    if r.get_id() == self._route_id: continue
                    print "       Also serves : Route: %s (%d) %d" % (r.get_name(), r.get_number(), r.get_id())

if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='List routes and stops per route')
   parser.add_argument("-r", "--route_id", help="Route ID", type=int)
   parser.add_argument("-d", "--dataset", help="june/july/brt/brt1", type=str, required=True)

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()
