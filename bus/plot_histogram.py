import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import math

from scipy.stats import pearsonr


class Runner(object):

    def __init__(self):

        print "run"

    def read_file(self, file_name, punt=5):

        data = []

        f = open(file_name)
        for line in f:
            # print line.strip()
            parts = line.split(",")

            da_id = int(parts[0].strip())
            value = float(parts[1].strip())

            #if value > 1.75:
            #     print "SKIPPING VALUE", value
            #     continue
            data.append((value, da_id))

            # data_ln.append(math.log(value))
        f.close()

        data.sort()
        for item in data:
            print item


        if punt > 0:
            data = data[:-punt]

        result = {}
        for item in data:
            result[item[1]] = item[0]

        return result


    def plot(self, dependant_var, other_var):

        data_dict = self.read_file(dependant_var, punt=10)

        other_dict = self.read_file(other_var,punt=0)

        print "plotting", dependant_var

        data = []
        other = []
        for da_id, v in data_dict.iteritems():
            o = other_dict.get(da_id)

            print v, o

            if v <0.025 or o == 0: continue

            other.append(o)
            data.append(v)

        data_ln = [math.log(v) for v in data]
        other_ln = [math.log(v) for v in other]

        #print data
        ave = sp.std(data)
        std_dev = sp.average(data)

        print ave, std_dev

        print "Pearsons R skewed", pearsonr(data, other)
        print "Pearsons R natlog", pearsonr(data_ln, other_ln)

        fig, ax = plt.subplots(figsize=(10, 6))

        # plt.hist(data_ln, normed=True, bins=30)
        ax.hist(data_ln, bins=30, rwidth=0.8, align="left")

        plt.title("DA Taps/Person (Sept. 2018 Weekdays 6AM-9AM)")
        plt.ylabel("Number of DAs")
        plt.xlabel("ln( Taps/Person )")

        plt.subplots_adjust(left=0.1, right=.9, top=0.9, bottom=0.1)
        plt.savefig('plot_da_histogram.png', bbox_inches='tight')
        plt.show()

        fig, ax = plt.subplots(figsize=(10, 6))
        plt.title("Accessibility Score vs Taps/Person (Sept. 2018 Weekdays 6AM-9AM)")
        plt.ylabel("Accessibility Score")
        plt.xlabel("Taps/Person")
        ax.scatter(data, other)

        plt.show()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(data_ln, other_ln)
        plt.title("Accessibility Score vs Taps/Person (Sept. 2018 Weekdays 6AM-9AM)")
        plt.ylabel("ln( Accessibility Score )")
        plt.xlabel("ln( Taps/Person )")
        plt.show()


if __name__ == "__main__":

    runner = Runner()
    runner.plot("scores_for_spss/sept_buffered_taps_per_pop.csv", "scores_for_spss/score_filt_freq_july_83.csv")
