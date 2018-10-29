def run():

    f = open("rand.txt")

    max_corr = None
    count = 0
    max_line = None

    for line in f:
        parts = line.split(",")

        try:
            c = float(parts[0].strip())
            count += 1
            if max_corr is None or c > max_corr:
                max_corr = c
                max_line = line
        except:
            pass
    f.close()

    print "Checked %d results" % count
    print "Line:", max_line
    print "MAX correlation", max_corr

if __name__ == "__main__":

    run()
