
class Intersect(object):

    def __init__(self, group1, group2, limit=None):

        self.group1_data = {}
        self.group2_data = {}

        self.group1 = group1
        self.group2 = group2

        self.process(group1, group2, limit=limit)

    def process(self, group1, group2, limit=None):

        # if limit is None or limit >= 2000:
        #     # print repr([k for k in group1.iterkeys()])
        #     print "start"
        #     a = hashlib.md5(repr(sorted([k for k in group1.iterkeys()]))).hexdigest()
        #     b = hashlib.md5(repr(sorted([k for k in group2.iterkeys()]))).hexdigest()
        #     c = hashlib.md5(a+b).hexdigest()
        #     print c

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


