import os

from route_id_names import ROUTE_IDS_05_04
from route_id_names import ROUTE_IDS_06_21

class TransitRoutes(object):

    def __init__(self, base_path):

        if base_path.find("2018_05_04") > 0:
            print "this is the JUNE data"
            self._include_route_dict = ROUTE_IDS_05_04
        elif base_path.find('2018_08_05'):
            print "this is the JULY data"
            self._include_route_dict = ROUTE_IDS_06_21
        else:
            raise ValueError("Invalid base path")

        self._base_path = base_path
        self._data = {}
        self._deprecated = {}
        self.read_file()

    def read_file(self):
        """
        0 route_id,
        1 route_type,
        2 route_color,
        3 text_color,
        4 name_short,
        5 name_long
        """
        file_name = os.path.join(self._base_path, "my-TransitRoutes.csv")

        line_count = 0
        f = None

        try:
            f = open(file_name, 'r')

            for line in f:
                line_count += 1
                if line_count == 1: continue

                line = line.strip()
                parts = line.split(",")

                route_id = int(parts[0].strip())
                short_name = parts[4].strip()
                long_name = parts[5].strip()

                # I am not sure what the route type is
                route_type = int(parts[1].strip())

                if route_type != 3:
                    raise ValueError("route type not 3")

                print "read route ID", route_id

                if not self._include_route_dict.has_key(route_id):
                    print "SKIPPING ROUTE", route_id
                    self._deprecated[route_id] = (short_name, long_name)
                    continue


                if self._data.has_key(route_id):
                    raise ValueError("THIS IS A DUP!!!")

                self._data[route_id] = (short_name, long_name)

            print "number of routes:", len(self._data)
            print "%s: read %d lines" % (file_name, line_count)

        finally:
            if f:
                print "closing file"
                f.close()

        # ----- TEST -----
        route_id_list = self.get_route_ids()
        s = []
        for route_id in route_id_list:
            name = self.get_route_name_from_id(route_id)
            s.append((name, route_id))

        s = sorted(s)
        for i, item in enumerate(s):
            print "%d ID: %s NAME: %s" % (i+1, item[1], item[0])
        # ---- END TEST -----

    def get_route_ids(self):
        result = [k for k in self._data.iterkeys()]
        return result

    def get_route_name_from_id(self, route_id):
        data = self._data.get(route_id)
        if data is None:
            return "Unknown: %s" % repr(route_id)
        return data[1]

    def get_route_number_from_id(self, route_id):
        data = self._data.get(route_id)
        if data is None:
            return "Unknown: %s" % repr(route_id)
        return data[0]
