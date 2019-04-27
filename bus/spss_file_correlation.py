import os
import numpy as np
from da_manager import DaData
from scipy.stats import pearsonr


#DEPENDANT_VAR =  'transit_ridership_percent'
#DEPENDANT_VAR =  'sept_taps_per_stop'
#DEPENDANT_VAR =  'sept_taps_per_pop'
#DEPENDANT_VAR = 'sept_taps_per_pop'
#DEPENDANT_VAR =  'jan_taps_per_stop'
#DEPENDANT_VAR =  'sept_user_percentage'
#DEPENDANT_VAR =  'jan_user_percentage'
DEPENDANT_VAR = 'sept_buffered_taps_per_pop'
#DEPENDANT_VAR = 'sept_buffered_users_per_pop'

SCORE_VAR = 'score_filt_freq_july_66'

class Runner(object):

    def __init__(self):


        self._dependant_col = None
        self._score_col = None

        self._data = []

    def remove_outliers_score(self, lines, score_col):

        skip_high = 5
        skip_low = 5

        x = []
        for index, line in enumerate(lines):
            parts = line.split(",")

            score = self.my_float(parts[score_col].strip())

            # print "ths is the score", score

            if score == 0:
                return

            x.append((score, line))

        x.sort()

        skip_high = len(x) - skip_high

        result = []
        for index, item in enumerate(x):

            if index < skip_low:
                print "SKIP LOW SCORE", item[0]
                continue

            if index >= skip_high:
                print "SKIP HIGH SCORE", item[0]
                continue

            result.append(item[1])
            # print item[0]

        # print result
        return result

    def remove_outliers_ridership(self, lines, dependent_col):

        skip_lower = 0
        skip_high = 10
        skip_over_percent = 100000.0
        skip_under_percent = 0.0

        skip_high_count = 0
        skip_low_count = 0

        bad_data_count = 0
        good_data = []

        for index, line in enumerate(lines):
            parts = line.split(",")

            try:
                dep_val = float(parts[dependent_col].strip())
                # print "DEP VALUE", dep_val

                if dep_val <= skip_under_percent:
                    skip_low_count += 1
                    # print "SKIPPING DEP VAR VALUE 0!!!!!!!!!"
                    continue

                if dep_val > skip_over_percent:
                    skip_high_count += 1
                    continue

                good_data.append(line)
            except:
                bad_data_count += 1
                print "GOT BAD DATA!!!!!", index, parts[dependent_col]

                # bad_data_index.append(index)

        skip_high_count += skip_high
        skip_low_count += skip_lower

        print "SKIP high count: %d" % (skip_high_count)
        print "SKIP low count: %d" % (skip_low_count)
        print "BAD count:", bad_data_count

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

    def remove_outliers(self, lines):

        lines = self.remove_outliers_ridership(lines, self._dependant_col)
        #lines = self.remove_outliers_score(lines, self._score_col)
        return lines


    def run(self):

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
                        self._dependant_col = i
                    elif header == SCORE_VAR:
                        self._score_col = i

            else:
                lines.append(line.strip())

        print "Considering %d of %d DAs" % (len(lines), (count - 1))
        f.close()
        lines = self.remove_outliers(lines)


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

        transit_ridership_data = data[:,self._dependant_col]

        # print transit_ridership_col
        # print transit_ridership_data

        result = []

        for col in xrange(col_count):
            # print "this is colunm", col
            if col == self._dependant_col:
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

        print "COLUMN                        PEARSON'S", DEPENDANT_VAR
        print "-----------------------------------------------------------"


        for item in result:
            p = item[0]
            score = p[1]

            if score >= 0:
                print "%-50s  %.3f" % (item[1], score)
            else:
                print "%-50s %.3f" % (item[1], score)

            # print item

    def my_float(self, input_str):

        try:
            result = float(input_str)
        except:
            result = 0
        return result

    def scatterplot(self, var1_name, var2_name):

        import matplotlib.pyplot as plt

        f = open("temp/spss.csv")
        lines = []
        count = 0

        for line in f:
            count += 1
            if count == 1: continue
            lines.append(line)

        f.close()

        lines = self.remove_outliers(lines)

        x = []
        y = []

        for line in lines:
            parts = line.split(",")

            x.append(self.my_float(parts[self._score_col]))
            y.append(self.my_float(parts[self._dependant_col]))

        fig, ax = plt.subplots(figsize=(10, 6))

        # for i in xrange(len(x)):
        #     print x[i], y[i]

        ax.scatter(x, y)

        plt.subplots_adjust(left=0.1, right=.9, top=0.9, bottom=0.1)

        plt.title("Taps per Person per DA vs. Accessibility Score")
        plt.ylabel("Taps per Person per DA ")
        plt.xlabel("Accessibility Score (Filtered Frequency)")

        plt.show()

if __name__ == "__main__":

    runner = Runner()
    runner.run()
    runner.scatterplot("score_filt_freq_july_40", DEPENDANT_VAR)
#    runner.display_result()

