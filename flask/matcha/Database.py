import pyodbc

# TODO define environment variables
# define server name, drive and database name
server = 'DESKTOP-C85GPRU'
database = 'MatchaDB'
driver = 'ODBC Driver 17 for SQL Server'


class Database:

    def __init__(self):
        self.conn = pyodbc.connect('DRIVER={' + driver + '}; \
                            SERVER=' + server + '; \
                            DATABASE=' + database + ';\
                            Trusted_Connection=yes;')
        self.cursor = self.conn.cursor()

    def get_cursor(self):
        return self.cursor
