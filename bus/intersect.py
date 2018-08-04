class Intersect(object):

    def __init__(self):

        self.group1_data = {}
        self.group2_data = {}

    def process(self, group1, group2):

        temp_count = 0
        for group1_id, polygon_1 in group1.iteritems():
            print "finding intersections for group1 id:", group1_id, polygon_1.get_area()
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

            # if temp_count == 10:
            #    break

        print "len(group1)", len(group1)
        print "len(group2)", len(group2)

    def get_intersections_for_group1_id(self, group1_id):

        result = []
        data = self.group1_data.get(group1_id, {})

        for group2_id, polygons in data.iteritems():
            for p in polygons:
                result.append((p, group2_id))
        return result

    def get_intersections_for_group2_id(self, group2_id):

        for k, v in self.group2_data.iteritems():
            print k, type(k), len(v)
        result = []
        data = self.group2_data.get(group2_id, {})

        for group1_id, polygons in data.iteritems():
            for p in polygons:
                result.append((p, group1_id))
        return result

