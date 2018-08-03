class Intersect(object):

    def __init__(self):

        self._data = {}

    def process(self, group1, group2):

        temp_count = 0
        for group1_id, polygon_1 in group1.iteritems():
            print "finding intersections for group1 id:", group1_id, polygon_1.get_area()
            for group2_id, polygon_2 in group2.iteritems():
                # print "    compare to group2 id:", group2_id, polygon_2.get_area()
                # Do these polygons intersect?
                intersection = polygon_1.intersect(polygon_2)

                if intersection:
                    data = self._data.get(group1_id, {})
                    data2 = data.get(group2_id, [])
                    for p in intersection:
                        print "  poly2 intersects poly1", p.get_area()
                        data2.append(p)
                    data[group2_id] = data2
                    self._data[group1_id] = data

            temp_count += 1

            if temp_count == 10:
                break

        print "len(group1)", len(group1)
        print "len(group2)", len(group2)

    def get_intersections_for_group1_id(self, group1_id):

        result = []
        data = self._data.get(group1_id)

        for group2_id, polygons in data.iteritems():
            result.extend(polygons)

        return result


