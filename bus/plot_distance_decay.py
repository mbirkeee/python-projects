import os
import matplotlib.pyplot as plt


class Runner(object):

    def __init__(self):

        pass

    def run(self):

        self._data = {}
        self.load_data_file("rand_stop_decay_150.txt")
        self.load_data_file("rand_stop_decay_250.txt")
        self.load_data_file("rand_stop_decay_400.txt")
        self.load_data_file("rand_stop_decay_600.txt")
        self.load_data_file("rand.txt")
#        self.load_data_file2("rand_vary_pow.txt")
        self.plot()


    def plot(self):

        fig, ax = plt.subplots()
        # line1, = ax.loglog(x, y, label="July")
        # line2, = ax.loglog(x2, y2, label="BRT 1")

        for key, result in self._data.iteritems():

            data = sorted(result)

            x = [item[0] for item in data]
            y = [item[1] for item in data]

            line1, = ax.plot(x, y, label=key)

        # line2, = ax.semilogy(x2, y2, label="BRT dpass = 250; Euclidian")


        ax.legend(loc='lower right')
        plt.title("Correlation vs Distance Decay")
        # plt.title("Correlation vs Population Factor")
        plt.ylabel("Correlation with actual ridership")
        plt.xlabel("Distance Decay (m)")
        # plt.xlabel("Population Factor (^pow)")
        plt.show()

    def load_data_file(self, filename):
        """
        Loop through all the lines, keep only those of interest
        """

        result = []
        f = open(filename, 'r')
        for line in f:
            line = line.strip()
            # print line

            parts = line.split(",")
            # print parts

            # print parts[0]
            # print parts[2]

            p = float(parts[0])

            decay = parts[2]
            parts = decay.split("_")

            # print "decay", parts[2]
            decay = float(parts[2].strip("'"))
            # print decay

            result.append((decay, p))
        f.close()

        self._data[filename] = result

    def load_data_file2(self, filename):
        """
        Loop through all the lines, keep only those of interest
        """

        result = []
        f = open(filename, 'r')
        for line in f:
            line = line.strip()
            # print line

            parts = line.split(",")
            # print parts

            # print parts[0]
            # print parts[2]

            p = float(parts[0])

            decay = parts[10]
            parts = decay.split("_")

            # print "decay", parts[2]
            decay = float(parts[2].strip("'"))
            # print decay

            result.append((decay, p))
        f.close()

        self._data[filename] = result

if __name__ == "__main__":

    runner = Runner()
    runner.run()
