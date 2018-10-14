import MySQLdb

class Runner(object):

    def __init__(self):
        pass

    def run(self):
        """
        Right now just conecting to locahost.
        Must port forward to mysql host

        ssh -g -L 3306:localhost:3306 mikeb@hazel4


        @article{LuoW.2003Mosa,
        issn = {02658135},
        journal = {Environment and Planning B: Planning and Design},
        pages = {865--884},
        volume = {30},
        publisher = {Pion Limited},
        number = {6},
        year = {2003},
        title = {Measures of spatial accessibility to health care in a GIS environment: Synthesis and a case study in the Chicago region},
        copyright = {Copyright 2017 Elsevier B.V., All rights reserved.},
        author = {Luo, W. and Wang, F.},
        keywords = {Architecture ; Sociology & Social History;},
        }

        """

        f = open("test_ref.bib", "w")

        config = {
    #        'host' : 'hazel4',
    #        'host' : '192.168.3.101',
            'host' : '127.0.0.1',
            'user' : 'root',
            'db' : 'ref_test',
            'passwd' : "Tab:1e",
            'charset' : 'utf8',
        }
        # db = MySQLdb.connect(host="127.0.0.1", user="root",
        #         db="ref_test", passwd="Tab:1e", charset= 'utf8',)

        db = MySQLdb.connect(**config)

        c = db.cursor()


        fields = [
            "id",               # 0
            "author",           # 1
            "year",             # 2
            "abstract",         # 3
            "secondary_title",  # 4
            "reference_type",   # 5
         ]

        formatted_fields = ",".join(fields)

        sql = "select %s from refs" % formatted_fields

        # print sql
        c.execute(sql)

        row_count = 0
        while True:
            row = c.fetchone()
            if row is None: break


            # First, make a key

            author = row[1]

            authors = author.split('\r')

            authors = [author.strip() for author in authors]
            year = row[2].strip()
            reference_type = row[5]

            key = self.make_key(authors, year)
            print key

            row_count += 1
            print authors,year,reference_type

            line = "@article{%s,\n" % key
            f.write(line.encode('utf-8'))

            author_str = self.make_author_str(authors)
            line = "author={%s},\n" % author_str
            f.write(line.encode('utf-8'))

            f.write("year={2018},\n")
            f.write("title={test title},\n")
            f.write("journal={test journal},\n")

            # End of entry
            f.write("}\n\n")

        f.close()
        print "read %d rows" % row_count

    def make_author_str(self, authors):

        return " and ".join(authors)

    def make_key(self, authors, year):

        key = ""

        for i, author in enumerate(authors):
            print "author", author
            parts = author.split(',')

            last_name = parts[0]

            key += last_name
            key += ":"

            if i == 1: break

        key += year
        key = key.replace(" ", "")
        return key

if __name__ == "__main__":
    runner = Runner()
    runner.run()
