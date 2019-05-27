import os

from da_manager import DaData

class Runner(object):

    def __init__(self):

        self.INCLUDE_COLS = [
            (  2, "pop_total"                           , None,                    ),
            (  2, "da_area_km2"                         , self.get_da_km2,         ),
            (  2, "pop_density_km2"                     , self.get_density,        ),
            (  3, "dwellings_total"                    , None,                    ),  # usually the same as dwellings occupied, or a couple more
            (  3, "dwellings_total_density_km2"         , self.get_density,         ),
            ( 17, "ave_household_size"                  , None,                      ),
            ( 18, "dwellings_occupied"                  , None,                      ),
            ( 18, "dwellings_occupied_density_km2"      , self.get_density,          ),
#            ( 19, "dwellings_occupied_detached"         , None                  ,       None),
            ( 19, "dwellings_occupied_detached_percent" , self.get_percentage ,      "dwellings_occupied" ),
            ( 20, "dwellings_occupied_highrise_percent" , self.get_percentage ,      "dwellings_occupied" ),
            ( 28, "married_percent"                     , self.get_percentage_pop,       ),
            ( 31, "education_no_highschool_percent"     , self.get_percentage_pop,       ),
            ( 33, "education_post_secondary_percent"    , self.get_percentage_pop,       ),
            ( 43, "employment_percent"                  , None,                    ),
            ( 52, "transit_ridership_percent"           , self.get_percentage_pop,         ),               # Verified that our data from DaMan is good
            ( 54, "cycle_percent"                       , self.get_percentage_pop,         ),
            ( 97, "median_total_income"                 , None,                         ),
            (120, "visible_minorities_percent"          , self.get_visible_minority_percentage,             ),
#            (118, "aboriginal"                         , None,                                                 ),
            (118, "aboriginal_percent"                  , self.get_percentage_pop,                              ),
            (122, "owner_percent"                       , self.get_percentage,      "dwellings_total"           ),
            (123, "renter_percent"                      , self.get_percentage,      "dwellings_total"           ),
        ]

        self._target_filename = None

        self._data_statscan = {}
        self._data_score_dict = {}
        # self._col_list = []
        self._da_list = None
        self._da_man = DaData()

        self._da_list = [da.get_id() for da in self._da_man.get_das()]
        self._da_list.sort()

        # for item in self._da_list:
        #     print item
        # raise ValueError("temp stop")

        self._column_data = {}

    def run(self):

        # self.load_road_length("/Users/michael/Downloads/totalrdlengthDA.csv")
        # raise ValueError("temp stop")

        # self.test_ridership_percentage()
        # raise ValueError("temp stop")

        self.load_statscan_headers("data/csv/statscan_da_data_headers.txt")
        self.load_statscan_data("data/csv/statscan_da_data.csv")
        self.load_da_scores("scores_for_spss")
        self.load_da_scores("scores_for_spss/permanent")

        self.merge()

    def get_da_km2(self, da_id, value, divide_by_col=None):

        da = self._da_man.get_da(da_id)
        area = da.get_area()
        # print "da area", area
        return area / 1000000.0

    def get_density(self, da_id, value, divide_by_col=None):
        """
        Generic density function that divides by DA area (km^2)
        """
        return  value / self.get_da_km2(da_id, None)

    def get_visible_minority_percentage(self, da_id, value, divide_by_col=None):
        """
        The statscan data is "not visible minority"
        """
        da = self._da_man.get_da(da_id)
        pop = da.get_population()
        p = 100.0 * float(value)/float(pop)

        not_p = 100.0 - p

        if not_p < 0.0:
            not_p = 0.0

        return not_p

    def get_percentage_pop(self, da_id, value, divide_by_col=None):
        da = self._da_man.get_da(da_id)
        pop = da.get_population()
        p = 100.0 * float(value)/float(pop)

        if p > 100.0:
            print "*"*80
            print "*"*80
            print "WARNING: Percentage > 100 for (population)", da_id, value, pop
            print "*"*80
            print "*"*80

        return p

    def get_percentage(self, da_id, value, divide_by_col=None):
        """
        Generic method to computed a percentage.

        NOTE: Its possible to get percentages > 100. e.g., brighton has 20
        occupied detached dwellings out of 17 dwellings total.
        """

        # print "want to divide value %f by column %s" % (value, repr(divide_by_col))

        if value == 0:
            return 0

        col_data = self._column_data.get(divide_by_col)
        divide_index = col_data.get('index')
        # print "The divide index is: %d" % divide_index

        parts = self._data_statscan.get(da_id)
        # print "the parts are", parts
        denominator = float(parts[divide_index])
        # print "the denominator is", denominator

        p = 100.0 * (float(value)/denominator)

        if p > 100.0:
            print "*"*80
            print "*"*80
            print "WARNING: Percentage > 100 for", da_id, value, divide_by_col
            print "*"*80
            print "*"*80

            p = 100.0

        return p

    def load_road_length(self, filename):
        """
        The raw data Sarah computed in ArcGIS is in m/m^2.
        We need to multiply by 1000 to convert to km/km^2
        """
        fout = open("roads_per_da_area.csv", "w")
        f = open(filename, "r")
        count = 0
        for line in f:
            count+=1
            if count == 1: continue

            print line
            parts = line.split(",")
            print parts

            fout.write("%s,%.3f\n" % (parts[1], float(parts[3]) * 1000.0 ))

        f.close()
        fout.close()

    def load_da_scores(self, dirname):

        files = os.listdir(dirname)
        for file in files:
            filename = '%s/%s' % (dirname, file)
            if file == 'README.txt':
                print "skipping file %s" % filename
                continue

            if not file.endswith(".csv"):
                print "skipping file", filename
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

            for col in self.INCLUDE_COLS:
                index = col[0]
                short_name = col[1]
                func = col[2]
                signature = "COL%d -" % index

                try:
                    divide_by_col = col[3]
                except:
                    divide_by_col = None

                if line.startswith(signature):
                    # print "KEEP LINE: %s" % line
                    # self._col_list.append((index, short_name, line))

                    print "ADDING INDEX", index, short_name, signature, line

                    self._column_data[short_name] = {
                        'index' : index,
                        'signature' : signature,
                        'desc' : line,
                        'func' : func,
                        'divide_by_col' : divide_by_col
                    }

        f.close()

        # for item in self._col_list:
        #     print item

        for key, value in self._column_data.iteritems():
            print "KEY", key, "VALUE", repr(value)

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


                # if da_id == 47110699:
                self._data_statscan[da_id] = parts

            except:
                pass

        f.close()

    def load_da_score_file(self, filename):

        print "load_da_score_file CALLED", filename

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

        self._target_filename = "temp/spss.csv"

        f = open(self._target_filename, "w")

        header =  "index,da_id"

        # Get a list of all the scores
        score_names = sorted(self._data_score_dict.keys())

        for score_name in score_names:
            header += ",%s" % score_name

        # Add the column names to the header
        col_names = [key for key in self._column_data.iterkeys()]
        col_names = sorted(col_names)

        for col_name in col_names:
            print col_name
            header += ",%s" % col_name

        f.write("%s\n" % header)

        # print "DA LIST:", len(self._da_list)
        # raise ValueError("temp stop")

        # Loop through all the detected da_ids
        for da_id in self._da_list:

            line = "%d,%d" % (index, da_id)

            for score_name in score_names:
                score_data = self._data_score_dict.get(score_name)
                score = score_data.get(da_id)
                line += ",%s" % score

            parts = self._data_statscan.get(da_id)

            for col_name in col_names:
                col_data = self._column_data.get(col_name)

                col_index = col_data.get('index')
                description = col_data.get('desc')
                func = col_data.get('func')

                try:
                    data = float(parts[col_index])
                except:
                    data = 0.0

                if func is not None:
                    divide_by_col = col_data.get('divide_by_col')
                    data = func(da_id, data, divide_by_col=divide_by_col)

#                pos = description.find(" - 25% sample")
                print "Data: %f Description: %s" % (data, description)

#                if pos > 0:
#                    data *= 4.0

                # Remove trailing zeros
                data_str = "%f" % data

                print "processing data", data

                # data_parts = data_str.split('.')
                # if len(data_parts) == 2:
                #     decimal = data_parts[1]
                #     if int(decimal[1:]) == 0:
                #         data = data_parts[0]

                line += ",%g" % data

            f.write("%s\n" % line)
            index += 1

        f.close()

        # f = open(target_filename, 'r')
        # for line in f:
        #     print line.strip()
        # f.close()


    def display_result(self):

        f = open(self._target_filename, 'r')
        line_count = 0
        col_titles = []
        for line in f:
            line_count += 1

            parts = line.split(',')
            parts = [item.strip() for item in parts]

            if line_count == 1:
                col_titles = parts
            else:
                print "-"*80
                for col_index, value in enumerate(parts):

                    print "%40s :   %s" % (col_titles[col_index], value)

        f.close()

    def test1(self):
        """
        compare the population and transit riders we got a year ago
        to the stuff in the latest downloaded statscan file.
        Looking for discrepancies
        """

        pop_col = self._column_data.get('pop_total')
        print pop_col
        pop_col_index = pop_col.get('index')

        transit_col = self._column_data.get('public_transit')
        print transit_col
        transit_index = transit_col.get('index')


        das = self._da_man.get_das()
        for da in das:

            da_id = da.get_id()

            parts = self._data_statscan.get(da_id)
            # print parts


            pop_1 = da.get_population()
            users_1 = da.get_transit_users()
            percent_1 = da.get_percent_transit_users()


            pop_2 = float(parts[pop_col_index])

            users_2 = float(parts[transit_index])

            # print "this is the type of pop_2", type(pop_2)

            # print da_id, pop_1, pop_2, users_1, percent_1

            if int(pop_1) != int(pop_2):
                raise ValueError("populations differ!!!!")

            print "DA: %s pop %5d (%5d) users %4d (%4d) percent %f" % (repr(da_id), int(pop_1), int(pop_2),
                                                                int(users_1), int(users_2), percent_1)



        for k in self._column_data.iterkeys():
            print k



if __name__ == "__main__":

    runner = Runner()
    runner.run()
    runner.display_result()

    # runner.test1()
