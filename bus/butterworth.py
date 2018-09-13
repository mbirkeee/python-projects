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

def norm(data):

    d = np.array(data)
    m_val = np.max(d)


    return d/m_val

def comp(per_hour, dpass):
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

if __name__ == "__main__":

    # comp(30, 15)
    # raise ValueError("done")

    # decay = get_factor(2, 15)
    # print decay
    # raise ValueError("Done")

    per_hour = np.array(range(1, 6000), dtype=np.float)
    per_hour = per_hour / 1000.0

    fig, ax = plt.subplots()
    line2, = ax.plot(per_hour, norm(per_hour), label="Departures / Hour")

    for dpass in [3, 5, 8, 10, 15, 20, 45, 60]:
        decay_list = []
        for f in per_hour:

            # decay = get_factor(f, dpass)
            decay = comp(f, dpass)
            # print f, decay
            decay_list.append(decay)
            label  = "Wait Time: %d min" % dpass

        line1, = ax.plot(per_hour, norm(decay_list), label=label)

    ax.legend(loc='lower right')
    plt.title("Service vs. Willing Wait Time (Butterworth)")
    plt.ylabel("Service")
    plt.xlabel("Departures / Hour")

    plt.show()





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
