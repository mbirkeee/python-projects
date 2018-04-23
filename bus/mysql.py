import MySQLdb

from password import MYSQL_PASSWORD

class MySQL(object):
    """
    Get MYSQL table contents and write into CSV file for local processing
    """
    def get_gps(self):

        db = MySQLdb.connect(host="crepe.usask.ca", user="slb405",
            db="SHED9", passwd="%s" % MYSQL_PASSWORD)

        c = db.cursor()

        sql = "select user_id, accu, lat, lon, provider, satellite_time, record_time from gps"

        c.execute(sql)

        f = open("gps_shed9.csv", "w")

        row_count = 0
        while True:
            row = c.fetchone()
            if row is None: break
            f.write("%s, %s, %s, %s, %s, %s, %s\n" % \
                    (row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            row_count += 1

        f.close()

    def get_battery(self):

        db = MySQLdb.connect(host="crepe.usask.ca", user="slb405", db="SHED9", passwd="%s" % MYSQL_PASSWORD)

        c = db.cursor()

        # sql = "select user_id, accu, lat, lon, provider, satellite_time from gps where user_id=1361"
        sql = "select user_id, record_time from battery"

        c.execute(sql)

        f = open("battery_shed9.csv", "w")

        row_count = 0
        while True:
            row = c.fetchone()
            if row is None: break

            f.write("%s, %s\n" % (row[0], row[1]))
            row_count += 1

        f.close()

if __name__ == "__main__":

    mysql = MySQL()
    mysql.get_battery()
    mysql.get_gps()


