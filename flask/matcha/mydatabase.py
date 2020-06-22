import pyodbc

# define server name, drive and database name
server = 'DESKTOP-4L29225\SQLEXPRESS'
database = 'MatchaDB'
driver = 'ODBC Driver 17 for SQL Server'

# # define a connection string
connection = pyodbc.connect('DRIVER={'+driver+'}; \
                            SERVER=' + server + '; \
                            DATABASE=' + database + ';\
                            Trusted_Connection=yes;')


class Database:

    def __init__(self):
        self.conn = connection

    def get_connection(self):
        return self.conn

    def add_user(self, details):
        cursor = self.conn.cursor()
        sql_query = '''INSERT INTO Users (Username, Password, FirstName, LastName, Email, Age)
                            VALUES ( ?, ?, ?, ?, ?, ?)'''
        user_info = (details['username'], details['password'], details['firstname'], details['lastname'],
                     details['email'], details['age'])

        cursor.execute(sql_query, user_info)
        cursor.commit()
        self.conn.close()

    def get_user_by_username(self, userDict):
        cursor = self.conn.cursor()
        username = userDict['username']
        sql_query = 'SELECT * FROM Users WHERE  Username = {})'.format(username)
        cursor.execute(sql_query)
        user = cursor.fetchall()
        self.conn.close()
        return user
