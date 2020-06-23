import pyodbc


class DATABASE:

    def __init__(self):
        # define server name, drive and database name
        server = 'PHETHOMA'
        database = 'MatchaDB'
        driver = 'ODBC Driver 17 for SQL Server'
        # # define a connection string
        self.__conn = pyodbc.connect('DRIVER={'+driver+'}; \
                                    SERVER=' + server + '; \
                                    DATABASE=' + database + ';\
                                    Trusted_Connection=yes;' )


    # Add the user the database
    def register_user(self, details):
        print(f"Register user... {details}")
        cursor = self.__conn.cursor()
        cursor.execute("""
        INSERT INTO Users (
            Username, 
            FirstName, 
            LastName, 
            Email, 
            Password, 
            Age
        ) VALUES (?,?,?,?,?,?)""" ,
        details['username'],
        details['firstname'],
        details['lastname'],
        details['email'],
        details['password'],
        details['age'])
        self.__conn.commit()
        # row = cursor.fetchone() # Throws exception

        # while row: 
        #     print('Inserted Product key is ' + str(row[0]))
        # self.__conn.close()
    

    # Get a single users information
    def get_user(self, query, fields=None):
        print(f"Single user... {query}")
        cursor = self.__conn.cursor()
        cursor.execute("""
        SELECT * FROM Users
        WHERE Username=?
        """, query['username'])
        user = cursor.fetchall()
        print(f"Debug {user}")
        # if not fields:
        #     user = self.__users.find_one(query)
        # else:
        #     user = self.__users.find_one(query, fields)

        return user

    
    # Get all the users from the database
	# def users(self, query={}):
    #     # print(f"All users... {query}")
        
    #     return "users"