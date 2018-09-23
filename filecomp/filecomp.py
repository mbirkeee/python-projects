import argparse
import os

class Runner(object):

    def __init__(self, args) :

        self._file_name = args.file_name
        self._file_count = 0
        self._line_count = 0
        self._in_dup_list = False
        self._duplicate_list = []
        self._dir_dict = {}
        self._dir_index = 1

        self._crc_to_file_map = {}
        self._file_to_crc_map = {}

        self._list_duplicates_dir_index = args.list_duplicates
        if self._list_duplicates_dir_index is None:
            self._list_duplicates_dir_index = 0

        self._move_duplicates_dir_index = args.move_duplicates
        if self._move_duplicates_dir_index is None:
            self._move_duplicates_dir_index = 0

        self._make_change = args.make_changes

    def run(self):

        print "move duplicate index", self._move_duplicates_dir_index
        print "make_changes", self._make_change

        # raise ValueError("temp stop")

        f = None
        try:
            f = open(self._file_name)

            for line in f:
                line = line.strip()
                self._line_count += 1
                if line.find('added file:') == 0:
                    # print line
                    line = line[len('added file:'):]
                    # print line
                    pos = line.find(", queue")
                    line = line[:pos]
                    # print line
                    line = line.strip()
                    line = line.strip("'")
                    # print ">>>%s<<<" % line

                    # raise ValueError("temp")
                    dir = os.path.dirname(line)
                    file = os.path.basename(line)

                    if file == '.DS_Store':
                        print "SKIPPING file: .DS_Store"
                        continue

#                    print "dir", dir
#                    print "file", file
#                    raise ValueError("temp stop")

                    self._file_count += 1

                    dir_data = self._dir_dict.get(dir, {})

                    if not dir_data.has_key('dir_index'):
                        dir_data['dir_index'] = self._dir_index
                        self._dir_index += 1

                    dir_files = dir_data.get('files', [])
                    dir_files.append(line)

                    dir_data['files'] = dir_files
                    self._dir_dict[dir] = dir_data
                elif line.find("dir_p:") == 0:
                    continue

                else:
                    if line.find('Duplicate files:') == 0:
                        self._in_dup_list = True

                        # Get the CRC for the duplicate files
                        parts = line.split(" ")
                        # print parts
                        crc = parts[5]
                        # raise ValueError('temp')

                    else:
                        if self._in_dup_list:
                            if len(line) > 0:
                                self._duplicate_list.append(line)

                                if not crc:
                                    raise ValueError("bad CRC!!!!")

                                self._file_to_crc_map[line] = crc
                                duplicate_files = self._crc_to_file_map.get(crc, [])
                                duplicate_files.append(line)
                                self._crc_to_file_map[crc] = duplicate_files

                            else:
                                self._in_dup_list = False
                                crc = None
                        else:
                            if len(line):
                                print "SKIPPING LINE", line

        finally:
            if f:
                f.close()


        # print repr(self._crc_to_file_map)

        move_duplicates = []

        for k, v in self._dir_dict.iteritems():
            current_dir_index = v.get('dir_index')
            print "DIR: (index: %d): %s" % (current_dir_index, k)
            print "  Files:      %8d" % len(v.get('files'))

            dup_count = 0
            for item in v.get('files'):
                # print "look for", item

                if item in self._duplicate_list:

                    if current_dir_index == self._move_duplicates_dir_index:
                        move_duplicates.append(item)

                    if current_dir_index == self._list_duplicates_dir_index:
                        my_crc = self._file_to_crc_map.get(item)

                        print "    File: %s" % item, my_crc

                        duplicate_files = self._crc_to_file_map.get(my_crc)
                        for dup in duplicate_files:
                            print "        - %s" % dup


                    dup_count += 1

            print "  Duplicates: %8d" % dup_count

        print "--- Done ---"

        if len(move_duplicates):
            for item in move_duplicates:
                self.move_to_duplicates_dir(item)

            if not self._make_change:
                print "*"*80
                print "Dry run only.  No changes made.  To actuall move files use -x option"
                print "*"*80

        print "--------"
        print "total file count:", self._file_count
        print "line count:", self._line_count
        print "number of duplicates:", len(self._duplicate_list)

    def move_to_duplicates_dir(self, item):
        print "MOVE:   ", item
        dir = os.path.dirname(item)
        file = os.path.basename(item)

        target_dir = os.path.join(dir, "duplicates")
        target = os.path.join(target_dir, file)
        print "TARGET: ", target

        if self._make_change:
            try:
                os.makedirs(target_dir)
            except:
                pass

            os.rename(item, target)

if __name__ == "__main__":

   parser = argparse.ArgumentParser(description='Summarize filecomp output')
   parser.add_argument("-f", "--file_name", help="filecomp output (with duplicates listed)", type=str, required=True)
   parser.add_argument("-m", "--move_duplicates", help="move duplicates into subdir for specified directory index", type=int, required=False)
   parser.add_argument("-d", "--list_duplicates", help="list duplicates for specified directory index", type=int, required=False)
   parser.add_argument("-x", "--make_changes", help="default is dry run", required=False, action='store_true')

   args = parser.parse_args()

   runner = Runner(args)
   runner.run()
