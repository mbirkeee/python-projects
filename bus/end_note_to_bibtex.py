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

        | id
       - | reference_type
        | text_styles
       - | author
       - | year
       - | title
       - | pages
       - | secondary_title
      -  | volume
       - | number
        | number_of_volumes
        | secondary_author
       - | place_published
       - | publisher
        | subsidiary_author
        | edition
      -  | keywords
        | type_of_work
      -  | date
      -  | abstract
        | label
       - | url
        | tertiary_title
        | tertiary_author
        | notes
        | isbn
        | alternate_title
        | accession_number
        | call_number
        | short_title
        | section
        | original_publication
        | reprint_edition
        | reviewed_item
        | author_address
        | image
        | caption
        | electronic_resource_number
        | link_to_pdf
        | translated_author
        | translated_title
        | name_of_database
        | database_provider
        | research_notes
        | language
        | access_date
        | last_modified_date
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
            "title",            # 6
            "abstract",         # 7
            "url",              # 8
            "place_published",  # 9
            "publisher",        # 10
            "pages",            # 11
            "volume",           # 12
            "keywords",         # 13
            "date",             # 14
            "number",           # 15
            "electronic_resource_number", #16
            "link_to_pdf",      # 17
            "notes",            # 18
            "isbn",             # 19
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

            if reference_type == 0:
                line = "@article{%s,\n" % key
                f.write(line.encode('utf-8'))

                # This is a journal
                journal = row[4]
                if journal:
                    line = "journal={%s},\n" % journal
                    f.write(line.encode('utf-8'))

            elif reference_type == 16: # I think this is "online
                line = "@online{%s,\n" % key
                f.write(line.encode('utf-8'))

            elif reference_type == 31: # I think this is "book". or maybe misc?  I did find that one was a book
                line = "@book{%s,\n" % key
                f.write(line.encode('utf-8'))

            elif reference_type == 33: # I think this is "book". or maybe misc?  I did find that one was a book
                line = "@misc{%s,\n" % key
                f.write(line.encode('utf-8'))

            elif reference_type == 3: #
                line = "@inproceedings{%s,\n" % key
                f.write(line.encode('utf-8'))

            elif reference_type == 10: # techreport I think
                line = "@techreport{%s,\n" % key
                f.write(line.encode('utf-8'))

                # publisher
                item = row[10]
                if item:
                    line = "institution={%s},\n" % item
                    f.write(line.encode('utf-8'))

            else:
                pass
            #     print row
            #     raise ValueError("cant handle ref type: %s" % repr(reference_type))


            # These are common to all types
            author_str = self.make_author_str(authors)
            line = "author={%s},\n" % author_str
            f.write(line.encode('utf-8'))

            f.write("year={%s},\n" % year)

            # Title
            title = row[6]
            if title:
                line = "title={%s},\n" % title
                f.write(line.encode('utf-8'))

            # Abstract
            item = row[7]
            if item:
                line = "abstract={%s},\n" % item
                f.write(line.encode('utf-8'))

            # URL
            item = row[8]
            if item:
                line = "url={%s},\n" % item
                f.write(line.encode('utf-8'))

            # location
            item = row[9]
            if item:
                line = "location={%s},\n" % item
                f.write(line.encode('utf-8'))

            # publisher
            item = row[10]
            if item:
                line = "publisher={%s},\n" % item
                f.write(line.encode('utf-8'))

            # pages
            item = row[11]
            if item:
                line = "pages={%s},\n" % item
                f.write(line.encode('utf-8'))

            # volume
            item = row[12]
            if item:
                line = "volume={%s},\n" % item
                f.write(line.encode('utf-8'))

            # keywords
            item = row[13]
            if item:
                keywords = self.make_keywords(item)
                line = "keywords={%s},\n" % keywords
                f.write(line.encode('utf-8'))

            # date
            item = row[14]
            if item:
                line = "date={%s},\n" % item
                f.write(line.encode('utf-8'))

            # number
            item = row[15]
            if item:
                line = "number={%s},\n" % item
                f.write(line.encode('utf-8'))

            # electronic resource number
            item = row[16]
            if item:
                line = "doi={%s},\n" % item
                f.write(line.encode('utf-8'))

            # link to PDF
            item = row[17]
            if item:
                file_path = self.make_file_path(item)

                line = "file={%s},\n" % file_path
                f.write(line.encode('utf-8'))

            # notes
            item = row[18]
            if item:
                line = "notes={%s},\n" % item
                f.write(line.encode('utf-8'))


            # isbn
            item = row[19]
            if item:
                line = "isbn={%s},\n" % item
                f.write(line.encode('utf-8'))
            # End of entry
            f.write("}\n\n")

        f.close()
        print "read %d rows" % row_count

    def make_keywords(self, input):

        keywords = input.split("\r")
        result = ",".join(keywords)
        print "keywords::::", result
        return result

    def make_file_path(self, item):
        print "MAKE PATH FOR:", item

        result = item.replace("internal-pdf://", "/Users/michael/PDF/")
        return result

    def make_author_str(self, authors):

        result =  " and ".join(authors)
        result.strip(",")
        result.strip(" ")
        result.strip(",")
        result.strip(" ")
        return result

    def make_key(self, authors, year):

        key = ""

        for i, author in enumerate(authors):
            # print "author", author
            parts = author.split(',')

            last_name = parts[0]

            key += last_name
            key += ":"

            if i == 1: break

        key += year
        key = key.replace(" ", "")

        # Unicode in citation keys is not supported... delete non ascii chars from key
        key = key.encode('ascii', 'ignore')
        print "KEY------>>", key
        # print "KEY------>>", key.encode('ascii', 'ignore')
        return key

if __name__ == "__main__":
    runner = Runner()
    runner.run()
