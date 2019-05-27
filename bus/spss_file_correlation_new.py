import os
import numpy as np
from da_manager import DaData
from scipy.stats import pearsonr
import scipy
import math
import copy

#DEPENDANT_VAR =  'transit_ridership_percent'
#DEPENDANT_VAR =  'jan_user_percentage'
#DEPENDANT_VAR =  'jan_taps_per_stop'

# DEPENDANT_VAR =  'sept_taps_per_stop'
# DEPENDANT_VAR =  'sept_taps_per_pop'
# DEPENDANT_VAR = 'sept_taps_per_pop'
# DEPENDANT_VAR =  'sept_user_percentage'
DEPENDANT_VAR = 'sept_buffered_taps_per_pop'
# DEPENDANT_VAR = 'sept_buffered_users_per_pop'

SCORE_VAR = 'score_filt_freq_july_40'

class Runner(object):

    def __init__(self):

        self._dependant_col = None
        self._score_col = None
        self._data = []

    def rm_discard(self, data1, data2, discard=5):
        data1 = copy.deepcopy(data1)
        data2 = copy.deepcopy(data2)
        sortable = []
        for i , d1 in enumerate(data1):
            d2 = data2[i]
            sortable.append((d1, d2))

        sortable.sort()
        for item in sortable:
            print item

        raise ValueError("temp stop")

    def rm_outliers(self, data1, data2, stdev_count=5.0):
        """
        This code removes any outliers more
        than some standard deviations away from average value
        """

        total_punt_count = 0
        for _ in xrange(15):

            data1 = copy.deepcopy(data1)
            data2 = copy.deepcopy(data2)

            data1_ave = scipy.mean(data1)
            data1_std = scipy.std(data1)

            data2_ave = scipy.mean(data2)
            data2_std = scipy.std(data2)

            data1_keep = []
            data2_keep = []

            punt_count = 0
            for i in xrange(len(data1)):
                value1 = data1[i]
                value2 = data2[i]

                if punt_count == 0:
                    if abs(value1 - data1_ave) > (stdev_count * data1_std):
                        # print "punt value1", value1, data1_ave, data1_std
                        punt_count += 1
                        total_punt_count += 1
                        continue


                    if abs(value2 - data2_ave) > (stdev_count * data2_std):
                        # print "punt value2", value2, data2_ave, data2_std
                        punt_count += 1
                        total_punt_count += 1
                        continue

                data1_keep.append(value1)
                data2_keep.append(value2)

            data1 = data1_keep
            data2 = data2_keep

            if punt_count == 0:
                # print "No punt; done"
                break

        print "total_punt_count", total_punt_count

        return data1_keep, data2_keep

    def logdata(self, data1, data2):
        keep1 = []
        keep2 = []

        discard_count = 0

        for i in xrange(len(data1)):
            value1 = data1[i]
            value2 = data2[i]

            if value1 < 0.025 or value2 < 0.025:
                discard_count += 1
                continue

            keep1.append(value1)
            keep2.append(value2)

        keep1 = [math.log(v) for v in keep1]
        keep2 = [math.log(v) for v in keep2]

        print "logdata discard count: %d" % discard_count
        return keep1, keep2

    def my_pearsonr(self, data1, data2, log=False, discard=None):

        if discard:
            data1, data2 = self.rm_discard(data1, data2, discard)
            result = pearsonr(data1, data2)
            return result
        # if outliers:
        #     data1, data

        if log:
            data1, data2 = self.logdata(data1, data2)
            data1, data2 = self.rm_outliers(data1, data2)
        else:
            data1, data2 = self.rm_outliers(data1, data2)

        print "DATA LEN", len(data1)
        result = pearsonr(data1, data2)
        return result


    def read_file(self):

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

        f.close()

        return headers, lines


    def run(self):

        headers, lines = self.read_file()

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

            # transit_ridership_data, c = self.rm_discard(transit_ridership_data, c, discard=2)

            r1 = self.my_pearsonr(transit_ridership_data, c)
            r2 = self.my_pearsonr(transit_ridership_data, c, log=True)
            # r3 = self.my_pearsonr(transit_ridership_data, c, discard=10)


            # print "pearsons", r
            header = headers[col]

            # r_ln = pearsonr(scipy.log(transit_ridership_data), scipy.log(c))

            r1 = (abs(r1[0]), r1[0])
            r2 = (abs(r2[0]), r2[0])
            result.append((r1, r2, header))

        result = sorted(result)
        result.reverse()

        print "COLUMN                        PEARSON'S", DEPENDANT_VAR
        print "-----------------------------------------------------------"


        for item in result:
            p = item[0]
            score = p[1]
            plog = item[1]
            score_log = plog[0]

            if score >= 0:
                print "%-50s  %.3f (%4.3f)" % (item[2], score, score_log)
            else:
                print "%-50s %.3f (%4.3f) "% (item[2], score, score_log)

            # print item

    def my_float(self, input_str):

        try:
            result = float(input_str)
        except:
            result = 0
        return result

    def analyze_score(self, score_col_name):

        headers, lines = self.read_file()

        temp = []
        for i, col_name in enumerate(headers):

            if col_name == "da_id":
                da_index = i
            if col_name == score_col_name:
                score_index = i

        for line in lines:
            parts = line.split(",")
            da_id = int(parts[da_index])
            score = float(parts[score_index])

            temp.append((score, da_id))

            # print da_id, score

        temp = sorted(temp, reverse=True)

        for i, item in enumerate(temp):
            print i, item

    def scatterplot(self, var1_name, var2_name, log=False):

        import matplotlib.pyplot as plt

        headers, lines = self.read_file()

        x = []
        y = []

        print "Considering %d lines" % len(lines)
        for line in lines:
            parts = line.split(",")

            # print parts
            # print "score col",parts[self._score_col], self._score_col
            # print "dep col", parts[self._dependant_col], self._dependant_col

            y.append(self.my_float(parts[self._score_col]))
            x.append(self.my_float(parts[self._dependant_col]))

        x, y = self.rm_outliers(x, y)

        if log:
            x, y = self.logdata(x, y)


        fig, ax = plt.subplots(figsize=(10, 6))

        # for i in xrange(len(x)):
        #     print x[i], y[i]

        ax.scatter(x, y)

        plt.subplots_adjust(left=0.1, right=.9, top=0.9, bottom=0.1)

        if log:
            plt.title("Taps per Person per DA vs. Accessibility Score (Nat. Log)")
            plt.xlabel("Taps per Person per DA (%s - Nat. Log)" % var2_name)
            plt.ylabel("Accessibility Score (%s - Nat. Log)" % var1_name)

            plt.savefig('plot_scatterplot_natlog.png', bbox_inches='tight')

        else:
            plt.title("Taps per Person per DA vs. Accessibility Score")
            plt.xlabel("Taps per Person per DA (%s)" % var2_name)
            plt.ylabel("Accessibility Score (%s)" % var1_name)

            plt.savefig('plot_scatterplot.png', bbox_inches='tight')

        plt.show()

if __name__ == "__main__":

    runner = Runner()
    runner.run()

    runner.analyze_score("score_filt_freq_july_40")
#    runner.scatterplot("score_filt_freq_july_40", DEPENDANT_VAR)
#    runner.scatterplot("score_filt_freq_july_40", DEPENDANT_VAR, log=True)
#    runner.display_result()

