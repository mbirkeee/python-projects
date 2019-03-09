
class Runner(object):

    def __init__(self):

        self._data_statscan = {}
        self._data_scores = []

        self._statscan_header = None

    def run(self):

        self.load_stats_can("/Users/michael/Downloads/AllDAdata2019march_data.csv")
        self.load_da_scores("temp/temp_scores_june.csv")
        self.merge()

    def load_stats_can(self, filename):
        print "called", filename

        expected_part_count = None

        f = open(filename, "r")
        for line in f:
            line = line.strip()

            if self._statscan_header is None:
                self._statscan_header = line

            parts = line.split(",")
            # print "PARTS", len(parts)
            part_count = len(parts)
            if expected_part_count is None:
                expected_part_count = part_count
            else:
                if part_count != expected_part_count:
                    raise ValueError("part count error")

            # print parts[0]
            try:
                da_id = parts[0].strip('"')
                da_id = int(da_id)
                # print "da id", da_id

                remainder = ",".join(parts[2:])

                self._data_statscan[da_id] = remainder
            except:
                pass

        f.close()

    def load_da_scores(self, filename):

        f = open(filename, "r")
        for line in f:
            line = line.strip()
            parts = line.split(",")
            #print parts
            da_id = parts[0].strip()
            da_id = int(da_id.strip("'"))

            score = parts[1].strip()
            score = score.strip("'")


            # print "DA ID", int(da_id)
            self._data_scores.append((da_id, score))
        f.close()

    def merge(self):

        index = 0

        f = open("temp/spss_2019_03_06.csv", "w")

        parts = self._statscan_header.split(",")
        header = ",".join(parts[2:])
        f.write("Index,DA_ID,Score,%s\n" % header)

        for item in self._data_scores:
            da_id = item[0]
            score = item[1]
            # print "DA_ID", da_id, "SCORE", score

            statscan_data = self._data_statscan.get(da_id)
            if statscan_data is None:
                raise ValueError("missing data: %d" % da_id)
            else:
                print "found data for", da_id

            f.write("%d,%d,%s,%s\n" % (index, da_id, score, statscan_data))

            index += 1
        f.close()


if __name__ == "__main__":

    runner = Runner()
    runner.run()
