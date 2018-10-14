import MySQLdb

def test():

    config = {
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

        year = row[2]
        row_count += 1
        print authors,year


    print "read %d rows" % row_count

if __name__ == "__main__":
    test()
