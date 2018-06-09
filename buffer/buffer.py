class Runner(object):
    """
     0, FID,
     1, FID_DA_CAN,
     2, DA_CANADAe,
     3, DA_CANAD_1,
     4, DA_CANAD_2,
     5, DA_CANAD_3,
     6, DA_CANAD_4,
     7, DA_CANAD_5,
     8, DA_CANAD_6,
     9, DA_CANAD_7,
    10, DA_CANAD_8,
    11, DA_CANAD_9,
    12, DA_CANA_10,
    13, DA_CANA_11,
    14, DA_CANA_12,
    15, DA_CANA_13,
    16, DA_CANA_14,
    17, DA_CANA_15,
    18, DA_CANA_16,
    19, DA_CANA_17,
    20, DA_CANA_18,
    21, DA_CANA_19,
    22, DA_CANA_20,
    23, DA_CANA_21,
    24, DA_CANA_22,
    25, Census_Dat,
    26, Census_D_1,
    27, FID_june20,
    28, lat,
    29, lon,
    30, x,
    31, y,
    32, BUFF_DIST,
    33, ORIG_FID
    """

    def __init__(self):
        #print "init called"

        self.data_dict = {}
        self.latlog_dict = {}

    def run(self):

        f = open("../../bus-data/buffer/junebuffer.txt", "r")

        count = 0
        for line in f:
            count += 1
            if count == 1: continue

            parts = line.split(",")

            da_fid = int(parts[1].strip())
            buf_fid = int(parts[27].strip())
            pop = int(parts[26].strip())
            lat = float(parts[28].strip())
            lon = float(parts[29].strip())

            # print da_fid, buf_fid, pop

            buf_data = self.data_dict.get(buf_fid, {})

            buf_data[da_fid] = pop

            self.data_dict[buf_fid] = buf_data
            self.latlog_dict[buf_fid] = (lat, lon)

        f.close()

        # print "read %d lines" % count

        print "buffer_fid,popsum,lat,lon"

        count = 0
        for buf_fid, buf_data in self.data_dict.iteritems():
            count += 1
            pop_total = 0
            # print count, buf_fid
            for da_fid, pop in buf_data.iteritems():
                # print "--", da_fid, pop
                pop_total += pop

            position = self.latlog_dict.get(buf_fid)

            print "%d,%d,%f,%f" % (buf_fid, pop_total, position[0], position[1])

if __name__ == "__main__":

    runner = Runner()
    runner.run()