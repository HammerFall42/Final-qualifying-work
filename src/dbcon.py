import psycopg2

class DBCon:
    def __init__(self):
        self.username = "postgres"
        self.password = "postgrepass"
        self.dbname = "ontologies"
        self.port = "5432"
        self.host = "127.0.0.1"

    def createConnection(self):
        return psycopg2.connect(
            database=self.dbname,
            user=self.username,
            password=self.password,
            host=self.host,
            port=self.port)

    def makeQuery(self, con, query, args=()):
        cur = con.cursor()
        cur.execute(query, args)
        r = [dict((cur.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur.fetchall()]
        cur.close()
        return r

    def selectInfo(self, tab, parent_id=-1):
        con = self.createConnection()
        query = "SELECT name, descr FROM " + tab
        if tab != "themes" and parent_id > 0:
            query += " WHERE parent_id = " + str(parent_id)
        return self.makeQuery(con, query, ())

    def selectById(self, id):
        con = self.createConnection()
        query = "SELECT name FROM second_level WHERE id = " + str(id)
        return self.makeQuery(con, query, ())