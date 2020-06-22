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


def get_connection():
    return connection


def add_user(details, conn):
    cursor = conn.cursor()
    sql_query = '''INSERT INTO Users (Username, Password, FirstName, LastName, Email, Age)
                        VALUES (%s, %s, %s, %s, %s, %s)'''
    user_info = (details['username'], details['firstname'], details['lastname'],
                 details['email'], details['age'])

    cursor.execute(sql_query, user_info)
    cursor.commit()
    conn.close()

def get_user_by_username(userDict, conn):
    cursor = conn.cursor()
    username = userDict['username']
    sql_query = 'SELECT * FROM Users WHERE  Username = {})'.format(username)
    cursor.execute(sql_query)
    user = cursor.fetchall()
    conn.close()
    return user