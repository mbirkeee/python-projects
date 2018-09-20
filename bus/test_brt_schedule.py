from data_manager import BrtSchedule
from data_manager import dataman_factory
from dataset import DATASET, SERVICES

class Runner(object):

    def __init__(self):

        # self._dataset = DATASET.BRT_1
        self._dataset = DATASET.JULY
        self._dataman = dataman_factory(self._dataset, link_stops=True, link_route_shapes=False)

    def get_stop_id(self, route):
        stops = route.get_stops()
        for stop in stops:
            # print "stop ID", stop.get_id()
            pass

        # Just return the Id of the last stop
        return stop.get_id()

    def test1(self):

        routes = self._dataman.get_routes()

        total_count = 0
        for route in routes:

            # stop_id = self.get_stop_id(route)

            stops = route.get_stops()

            # print "STOP ID", stop_id

            print route.get_id(), route.get_number(), route.get_name()
            for service in SERVICES:
                for t in ["5", "8:30", "15", "19:45"]:
                # for t in ["8:30"]:
                    for stop in stops:
                        stop_id = stop.get_id()
                        result = self._dataman.get_departs_per_hour(route, stop_id, service, t)
                        print "HOUR: stop_id: %d route: %d service: %d time: %s departs: %f" % (stop_id, route.get_id(), service, t, result)
                        total_count += 1

            #    result = self._dataman.get_departs_per_day(route, stop_id, service)
            #    print "DAY: route: %d service: %d departs: %f" % (route.get_id(), service, result)

            # result = self._dataman.get_departs_per_week(route, stop_id)
            # print "WEEK: route: %d departs: %f" % (route.get_id(), result)
        print "Ran %d tests" % total_count

if __name__ == "__main__":

    runner = Runner()
    runner.test1()
