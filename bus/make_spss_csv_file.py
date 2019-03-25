import os

# List of columns from the statscan data file to include in our CSV file

INCLUDE_COLS = [
    (  2, "total_pop"),
    (  3, "private_dwellings"),
    ( 17, "ave_household_size"),
    ( 18, "dwellings"),
    ( 19, "detached"),
    ( 20, "highrise"),
    ( 28, "married"),
    ( 31, "no_highschool"),
    ( 33, "post_secondary"),
    ( 43, "employment_rate"),
    ( 54, "bike_to_work"),
    ( 97, "median_total_income"),
    (119, "visible_minorities"),
    (117, "aboriginal"),
    (122, "owner"),
    (123, "renter"),

]

class Runner(object):

    def __init__(self):

        self._data_statscan = {}
        self._data_score_dict = {}
        self._col_list = []
        self._da_list = None

    def run(self):

        self.load_statscan_headers("data/csv/statscan_da_data_headers.txt")
        self.load_statscan_data("data/csv/statscan_da_data.csv")
        self.load_da_scores("scores_for_spss")
        self.merge()

    def load_da_scores(self, dirname):

        files = os.listdir(dirname)
        for file in files:
            filename = '%s/%s' % (dirname, file)
            if file == 'README.txt':
                print "skipping file %s" % filename
                continue

            print "CONSIDER FILE", filename

            parts = file.split('.')
            col_name = parts[0]

            print "col_name", col_name

            scores = self.load_da_score_file(filename)
            self._data_score_dict[col_name] = scores

    def load_statscan_headers(self, filename):
        """
        Loop through all the lines, keep only those of interest
        """
        f = open(filename, 'r')
        for line in f:
            line = line.strip()

            for col in INCLUDE_COLS:
                index = col[0]
                short_name = col[1]
                signature = "COL%d -" % index

                if line.startswith(signature):
                    # print "KEEP LINE: %s" % line
                    self._col_list.append((index, short_name, line))

        f.close()

        for item in self._col_list:
            print item

    def load_statscan_data(self, filename):
        print "called", filename

        expected_part_count = None

        f = open(filename, "r")
        for line in f:
            line = line.strip()

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
                self._data_statscan[da_id] = parts

            except:
                pass

        f.close()

    def load_da_score_file(self, filename):

        da_list = []

        data = {}

        f = open(filename, "r")
        for line in f:
            line = line.strip()
            parts = line.split(",")
            #print parts
            da_id = parts[0].strip()
            da_id = int(da_id.strip("'"))

            da_list.append(da_id)

            score = parts[1].strip()
            score = score.strip("'")

            # print "DA ID", int(da_id)
            data[da_id] = score

        f.close()

        if self._da_list is None:
            self._da_list = sorted(da_list)

            # for item in self._da_list:
            #     print item

        return data

    def merge(self):

        index = 0

        target_filename = "temp/spss_2019_03_06.csv"
        f = open(target_filename, "w")

        header =  "index,da_id"

        # Get a list of all the scores
        score_names = sorted(self._data_score_dict.keys())

        for score_name in score_names:
            header += ",%s" % score_name

        # Add the column names to the header
        for col in self._col_list:
            short_name = col[1]
            header += ",%s" % short_name

        f.write("%s\n" % header)

        # Loop through all the detected da_ids
        for da_id in self._da_list:

            line = "%d,%d" % (index, da_id)

            for score_name in score_names:
                score_data = self._data_score_dict.get(score_name)
                score = score_data.get(da_id)
                line += ",%s" % score


            parts = self._data_statscan.get(da_id)

            for col in self._col_list:
                col_index = col[0]
                description = col[2]
                data = parts[col_index]

                pos = description.find(" - 25% sample")
                print "This is the description", pos, description

                if pos > 0:
                    try:
                        print "Went to multiply '%s' by 4" % data
                        data = float(data) * 4.0
                        data = "%f" % data
                    except:
                        data = ''

                # Remove trailing zeros
                data_parts = data.split('.')
                if len(data_parts) == 2:
                    decimal = data_parts[1]
                    if int(decimal[1:]) == 0:
                        data = data_parts[0]

                line += ",%s" % data

            f.write("%s\n" % line)
            index += 1

        f.close()

        f = open(target_filename, 'r')
        for line in f:
            print line.strip()
        f.close()

if __name__ == "__main__":

    runner = Runner()
    runner.run()
