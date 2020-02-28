# Author: Arjun Menon <amm8987@psu.edu>

"""
This file contains function to interface with MongoDB
"""

from mysql import connector
from mysql.connector import errorcode


# Connect to DB Instance
def connect_db(user, password, database, host='localhost'):
    try:
        con = connector.connect(user=user, password=password, host=host, database=database)
        return con
    except connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)


