def run():

    f = open("rand.txt")

    max_corr = None
    count = 0
    max_line = None


    result = []

    for line in f:

        # print line
        # if count > 10: break

        parts = line.split(",")


        # Get the correlation coefficient
        try:
            c = float(parts[0].strip())

            result.append((c, parts))

            count += 1
            if max_corr is None or c > max_corr:
                max_corr = c
                max_line = line
        except:
            pass
    f.close()

    result = sorted(result)

    for index, item in enumerate(result):
        print_item(index, item)


#     print "Checked %d results" % count
#     print "Line:", max_line
#     print "MAX correlation", max_corr



def print_item(index, item):

    line = "%d: %.4f" % (index, item[0])
    # print item

    line += " Dist Decay: %4d" % get_dist_decay(item[1])
    line += " Stop Dmd: %4d" % get_stop_demand(item[1])
    line += " Dmd Methd: %0.4f" % get_demand_method(item[1])
    line += " Clip: %0.4f" % get_raster_clip(item[1])
    line += " Score: %s" % get_score_method(item[1])
    line += " Wait bpass: %0.4f" % get_wait_bpass(item[1])
    print line

def get_demand_method(parts):

    for part in parts:
        if part.find("demand_method") > 0:
            things = part.split(":")
            values = things[1].split("_")
#            print "VALUES1: >>%s<<" % values[1]
            return float(values[1].strip("'"))

    return 0

def get_wait_bpass(parts):

    for part in parts:
        if part.find("wait_bandpass") > 0:
            things = part.split(":")
            return float(things[1])

    return 0


def get_score_method(parts):

    for part in parts:
        if part.find("score_method") > 0:
#            print "demad part >>%s<<" % part
            things = part.split(":")
            method = things[1].strip()
            method = method.strip("}")

            return method

    return "Unknown"

def get_raster_clip(parts):

    for part in parts:
        if part.find("raster_clip") > 0:
            things = part.split(":")

            value = things[1].strip().strip("'")

            try:
                return float(value)
            except:
                stuff = value.split("_")
                return float(stuff[1].strip(''))
    return 0


def get_dist_decay(parts):

    for part in parts:
        if part.find("distance_decay") > 0:
            result = int(''.join(c for c in part if c.isdigit()))
            return result

    return 0

def get_stop_demand(parts):

    for part in parts:
        if part.find("stop_demand") > 0:
            result = int(''.join(c for c in part if c.isdigit()))
            return result

    return 0


if __name__ == "__main__":

    run()
