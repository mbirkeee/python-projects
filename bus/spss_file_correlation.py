import os
import numpy as np
from da_manager import DaData
from scipy.stats import pearsonr


# DEPENDANT_VAR =  'transit_ridership_percent'
DEPENDANT_VAR =  'sept_taps_per_stop'
#DEPENDANT_VAR =  'sept_taps_per_pop'
#DEPENDANT_VAR =  'jan_taps_per_stop'
#DEPENDANT_VAR =  'sept_user_percentage'
#DEPENDANT_VAR =  'jan_user_percentage'

class Runner(object):

    def __init__(self):

        self._data = []

    def remove_outliers(self, lines, dependent_col):

        skip_lower = 10
        skip_high = 5

        good_data = []

        for index, line in enumerate(lines):
            parts = line.split(",")

            try:
                dep_val = float(parts[dependent_col].strip())
                # print "DEP VALUE", dep_val
                good_data.append(line)
            except:
                pass
                # print "GOT BAD DATA!!!!!", index
                # bad_data_index.append(index)

        x = []

        for line in good_data:
            parts = line.split(",")
            dep_val = float(parts[dependent_col].strip())
            x.append((dep_val, line))

        result = []

        x.sort()

        skip_high = len(x) - skip_high

        for index, item in enumerate(x):

            if index < skip_lower:
                # print "SKIP LOW VALUE"
                continue

            if index >= skip_high:
                # print "SKIP HIGH VALUE"
                continue

            result.append(item[1])
            # print item[0]

        return result


    def run(self):

        transit_ridership_col = None

        count = 0
        f = open("temp/spss.csv")
        lines = []

        for line in f:
            count += 1
            parts = line.split(",")

            if count == 1:
                headers = [part.strip() for part in parts]

                for i, header in enumerate(headers):
                    if header == DEPENDANT_VAR:
                        transit_ridership_col = i
                        break

            else:
                lines.append(line.strip())

        print "Considering %d of %d DAs" % (len(lines), (count - 1))
        f.close()

        lines = self.remove_outliers(lines, transit_ridership_col)
        print "Considering %d of %d DAs" % (len(lines), (count - 1))

        row_count = len(lines)
        col_count = len(headers)

        # print "rows, cols", row_count, col_count

        data = np.zeros((row_count, col_count))

        row = 0
        for line in lines:

            parts = line.split(",")

            for col, value in enumerate(parts):
                if value is None or value == "None":
                    value = "0"

                value = float(value.strip())
                # print row, col, value
                data[row, col] = value
            row += 1

        # print data.shape

        transit_ridership_data = data[:,transit_ridership_col]

        # print transit_ridership_col
        # print transit_ridership_data

        result = []

        for col in xrange(col_count):
            # print "this is colunm", col
            if col == transit_ridership_col:
                continue

            # c = data[:,col:col+1]
            c = data[:,col]
            # print c.shape

            r = pearsonr(transit_ridership_data, c)
            # print "pearsons", r
            header = headers[col]

            r = (abs(r[0]), r[0])
            result.append((r, header))

        result = sorted(result)
        result.reverse()

        print "COLUMN                                           PEARSON'S", DEPENDANT_VAR
        print "-----------------------------------------------------------"


        for item in result:
            p = item[0]
            score = p[1]

            if score >= 0:
                print "%-50s  %.3f" % (item[1], score)
            else:
                print "%-50s %.3f" % (item[1], score)

            # print item

if __name__ == "__main__":

    runner = Runner()
    runner.run()
#    runner.display_result()

