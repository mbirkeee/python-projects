def run():

    f = open("rand.txt")

    max_corr = None

    for line in f:
        parts = line.split(",")

        try:
            c = float(parts[0].strip())

            if max_corr is None or c > max_corr:
                max_corr = c
        except:
            pass
    f.close()

    print "MAX correlation", max_corr
    
if __name__ == "__main__":

    run()
