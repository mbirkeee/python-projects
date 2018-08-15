class Intersect(object):

    def __init__(self, group1, group2, limit=None):

        self.group1_data = {}
        self.group2_data = {}

        if not isinstance(group1, list):
            group1 = [group1]

        if not isinstance(group2, list):
            group2 = [group2]

        self.group1 = group1
        self.group2 = group2

        self._total_count = 0
        self._temp_count = 0

        self._group1_id_map = {}
        self._group2_id_map = {}

        self.process(group1, group2, limit=limit)

    def _count(self):
        self._total_count += 1
        self._temp_count += 1
        if self._temp_count >= 1000:
            print "Detected %d intersections..." % self._total_count
            self._temp_count = 0

    def process(self, group1, group2, limit=None):

        test_shapefile_list = []

        temp_count = 0
        for item1 in group1:
            group1_id = item1.get_id()
            polygon_1 = item1.get_polygon()

            self._group1_id_map[group1_id] = item1

            # print "finding intersections for group1 id:", group1_id

            for item2 in group2:
                group2_id = item2.get_id()
                polygon_2 = item2.get_polygon()
                self._group2_id_map[group2_id] = item2
                # print "    compare to group2 id:", group2_id, polygon_2.get_area()
                # Do these polygons intersect?

                intersection = polygon_1.intersect(polygon_2)

                if intersection:
                    data = self.group1_data.get(group1_id, {})
                    data2 = data.get(group2_id, [])
                    for p in intersection:
                        # print "  poly2 intersects poly1", p.get_area()
                        data2.append(p)
                        self._count()

                    data[group2_id] = data2
                    self.group1_data[group1_id] = data

                    data = self.group2_data.get(group2_id, {})
                    data2 = data.get(group1_id, [])
                    for p in intersection:
                        data2.append(p)
                        # self._count()
                    data[group1_id] = data2
                    self.group2_data[group2_id] = data

            temp_count += 1

            if limit and temp_count >= limit:
                print "terminate early at limit", limit
                break

        print "Intersect: group_1: %d group_2: %d intersections: %d" % \
              (len(group1), len(group2), self._total_count)

    def get_intersections(self, group=1, id=None):
        if group == 1:
            return self.get_intersections_for_group1_id(id)
        else:
            return self.get_intersections_for_group2_id(id)

    def get_intersections_for_group1_id(self, group1_id):

        result = []
        data = self.group1_data.get(group1_id, {})

        for group2_id, polygons in data.iteritems():
            item = self._group2_id_map.get(group2_id)
            for p in polygons:
                result.append((p, group2_id, item))
        return result

    def get_intersections_for_group2_id(self, group2_id):

        result = []
        data = self.group2_data.get(group2_id, {})

        for group1_id, polygons in data.iteritems():
            item = self._group1_id_map.get(group1_id)
            for p in polygons:
                result.append((p, group1_id, item))
        return result

    def get_group1_ids(self):
        return [id for id in self.group1_data.iterkeys()]

    def get_group2_ids(self):
        return [id for id in self.group2_data.iterkeys()]




class IntersectOLD(object):

    def __init__(self, group1, group2, limit=None):

        self.group1_data = {}
        self.group2_data = {}

        self.group1 = group1
        self.group2 = group2

        self.process(group1, group2, limit=limit)

    def process(self, group1, group2, limit=None):

        temp_count = 0
        for group1_id, polygon_1 in group1.iteritems():
            print "finding intersections for group1 id:", group1_id
            for group2_id, polygon_2 in group2.iteritems():
                # print "    compare to group2 id:", group2_id, polygon_2.get_area()
                # Do these polygons intersect?

                intersection = polygon_1.intersect(polygon_2)

                if intersection:
                    data = self.group1_data.get(group1_id, {})
                    data2 = data.get(group2_id, [])
                    for p in intersection:
                        # print "  poly2 intersects poly1", p.get_area()
                        data2.append(p)
                    data[group2_id] = data2
                    self.group1_data[group1_id] = data

                    data = self.group2_data.get(group2_id, {})
                    data2 = data.get(group1_id, [])
                    for p in intersection:
                        data2.append(p)
                    data[group1_id] = data2
                    self.group2_data[group2_id] = data

            temp_count += 1

            if limit and temp_count >= limit:
                print "terminate early at limit", limit
                break



        print "len(group1)", len(group1)
        print "len(group2)", len(group2)

    def get_intersections(self, group=1, id=None):
        if group == 1:
            return self.get_intersections_for_group1_id(id)
        else:
            return self.get_intersections_for_group2_id(id)

    def get_intersections_for_group1_id(self, group1_id):

        result = []
        data = self.group1_data.get(group1_id, {})

        for group2_id, polygons in data.iteritems():
            for p in polygons:
                result.append((p, group2_id))
        return result

    def get_intersections_for_group2_id(self, group2_id):

        result = []
        data = self.group2_data.get(group2_id, {})

        for group1_id, polygons in data.iteritems():
            for p in polygons:
                result.append((p, group1_id))
        return result

    def get_group1_ids(self):
        return [id for id in self.group1_data.iterkeys()]

    def get_group2_ids(self):
        return [id for id in self.group2_data.iterkeys()]


