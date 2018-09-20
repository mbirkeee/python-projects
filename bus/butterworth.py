import math
import random
import matplotlib.pyplot as plt
import numpy as np
from scipy import special

class Filter(object):

    def __init__(self, dpass=250, e=1, n=6):
        self._dpass = dpass
        self._e = e
        self._n = n

    def set_dpass(self, dpass):
        self._dpass = dpass

    def butterworth(self, distance):

        r = float(distance)/float(self._dpass)
        rp = math.pow(r, self._n)
        result = 1.0 / math.sqrt(1.0 + self._e * rp)
        return result

    def run(self, distance):
        return self.butterworth(distance)


def get_factor(busses_per_hour, dpass):

    interval = 60.0 / float(busses_per_hour)

    filter = Filter(dpass = dpass)
    total = 0.0

    if dpass == 1:
        runs = 1000000
    else:
        runs = 100000

    for i in xrange(runs):

        wait_time = random.randint(0, int(100.0 * interval)) / 100.0

        factor = filter.butterworth(wait_time)
        total += factor
        # print wait_time, factor

    average =  total/float(runs)
    return average

def normalize(data):

    d = np.array(data)
    m_val = np.max(d)


    return d/m_val

def wait_decay(per_hour, dpass):
    """
    Compute the area under butterworth filter with x=1 and n=6
    """
    d = 60.0 / per_hour

    d2 = math.pow(d, 2)
    d4 = math.pow(d, 4)
    d6 = math.pow(d, 6)

    dpass2 = math.pow(dpass, 2)
    dpass4 = math.pow(dpass, 4)
    dpass6 = math.pow(dpass, 6)

    sqrt3 = math.sqrt(3.0)

    m = (sqrt3 + 2.0) / 4.0

    cos_top = dpass2 - (sqrt3 - 1.0) * d2
    cos_bottom = (1.0 + sqrt3) * d2 + dpass2

    x = math.acos(cos_top/cos_bottom)

    elip = special.ellipkinc(x, m)

    top1 = d4 - dpass2 * d2 + dpass4
    bottom1 = (1.0 + sqrt3) * d2 + dpass2
    bottom1 = math.pow(bottom1, 2.0)

    part = math.sqrt(top1/bottom1)

    top = 5.0 * math.pow(3.0, 0.75) * d * (d2 + dpass2) * part * elip

    top2 = d2 * (d2 + dpass2)
    bottom2 = (1.0 + sqrt3) * d2 + dpass2
    bottom2 = math.pow(bottom2, 2.0)

    part2 = 2.0 * math.sqrt(top2/bottom2)

    bottom = part2 * math.sqrt(d6 + dpass6)
    final_area = top / bottom
    result =  final_area / d

    return result

def plot_butterworth_wait():

    wait_time = np.array(range(0, 600), dtype=np.float)
    wait_time /= 10.0

    fig, ax = plt.subplots(figsize=(10, 6))

    filter = Filter()

    mb = [1, 2, 5, 10, 15, 20, 30, 45, 60]

    for m in mb:
        result = []
        filter.set_dpass(m)

        for t in wait_time:
            decay = filter.butterworth(t)
            result.append(decay)

        line2, = ax.plot(wait_time, result, label="mb: %d mins" % m)

    ax.legend(loc='upper right')
    plt.title("Decay vs. Wait Time (minutes)")
    plt.ylabel("Decay Value")
    plt.xlabel("Wait Time (minutes)")
    plt.subplots_adjust(left=0.1, right=.9, top=0.9, bottom=0.1)
    plt.show()


def plot_butterworth(dpass):

    d = np.array(range(0, 500), dtype=np.float)
    filter = Filter(dpass=dpass)

    result = []
    for dist in d:
        decay = filter.butterworth(dist)
        result.append(decay)

    fig, ax = plt.subplots(figsize=(10, 6))
    line2, = ax.plot(d, result, label="dpass = 250 meters")

    ax.legend(loc='lower left')
    plt.title("Decay vs. Distance with Butterworth Filter")
    plt.ylabel("Decay Value")
    plt.xlabel("Distance (meters)")
    plt.show()

def plot_wait(norm=False):

    per_hour = np.array(range(1, 6000), dtype=np.float)
    per_hour = per_hour / 1000.0

    fig, ax = plt.subplots(figsize=(10, 6))

    for dpass in [1, 2, 5, 10, 15, 20, 30, 45, 60]:
        decay_list = []
        for f in per_hour:

            # decay = get_factor(f, dpass)
            decay = wait_decay(f, dpass)
            # print f, decay
            decay_list.append(decay)

        label  = "m_b: %d (min)" % dpass

        if norm:
            line1, = ax.plot(per_hour, normalize(decay_list), label=label)
        else:
            line1, = ax.plot(per_hour, decay_list, label=label)
        # line1, = ax.plot(mi, decay_list, label=label)

    if norm:
        line2, = ax.plot(per_hour, normalize(per_hour), label="Departures / Hour")

    if norm:
        ax.legend(loc='lower right')
        plt.title("Normalized Service vs. Departures per Hour")
        plt.ylabel("Normalized Service")
    else:
        ax.legend(loc='upper left')
        plt.title("Service vs. Departures per Hour")
        plt.ylabel("Service")

    plt.xlabel("Departures / Hour")

    plt.subplots_adjust(left=0.1, right=.9, top=0.9, bottom=0.1)

    plt.show()

if __name__ == "__main__":

    plot_wait(norm=True)

    # plot_butterworth_wait()
    # comp(30, 15)
    # raise ValueError("done")

    # decay = get_factor(2, 15)
    # print decay
    # raise ValueError("Done")






"""
 fig, ax = plt.subplots()
    # line1, = ax.loglog(x, y, label="July")
    # line2, = ax.loglog(x2, y2, label="BRT 1")

    line1, = ax.semilogy(x, y, label="July")
    line2, = ax.semilogy(x2, y2, label="BRT 1")

    ax.legend(loc='lower left')
    plt.title("Score vs # of Grid Cells")
    plt.ylabel("Accessibility Score")
    plt.xlabel("Number of 100m X 100m grid Cells")
    plt.show()

"""
