import os
import simplejson

class Runner(object):
    """
    This utility reads in all the transit score CSV files downloaded from
    walkscore and makes a CSV file of the results.

    It really only needs to be run one time to produce the CSV file which
    will then be checked into git
    """
    def __init__(self):
        pass

    def run(self):

        base_dir = "temp/transit_score"
        files = os.listdir(base_dir)

        target_file = "data/csv/transit_score_100.csv"

        f_out = open(target_file, "w")
        f_out.write("index,da_id,raster_id,transit_score,routes_nearby\n")

        for index, file in enumerate(files):
            # print file, type(file)
            parts = file.split("_")
            # print parts
            da_id = int(parts[0])

            parts = parts[1].split(".")
            raster_id = int(parts[0])

            file_name = "%s/%s" % (base_dir, file)
            f = open(file_name, "r")
            data = simplejson.load(f)
            f.close()

            # for k, v in data.iteritems():
            #     print k, v

            transit_score = int(data.get('transit_score'))
            summary = data.get('summary')
            # print "summary", summary
            parts = summary.split(":")
            parts = parts[1].strip().split(" ")
            # print parts
            nearby_bus_routes = int(parts[0])

            print "index", index, "da_id", da_id, "raster_id", raster_id, \
                "transit_score", transit_score, "nearby bus routes", nearby_bus_routes

            f_out.write("%d,%d,%d,%d,%d\n" % (index, da_id, raster_id, transit_score, nearby_bus_routes) )

        f_out.close()

if __name__ == "__main__":

    runner = Runner()
    runner.run()
