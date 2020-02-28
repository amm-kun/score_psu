# Author: Arjun Menon <amm8987@psu.edu>

"""
This file contains function to interface with MongoDB
"""

from pymongo import MongoClient
from pymongo import errors


# Connect to DB Instance
def connect_db(db, host='localhost', port='27017'):
    client = MongoClient(host, port)
    try:
        db_obj = client[db]
        return db_obj, client
    except errors.PyMongoError as e:
        print(e)


# Single insert into collection
def insert_record(db_obj, collection, record):
    records = db_obj[collection]
    try:
        result = records.insert_one(record)
        print("Insert successful with ID: ", result.inserted_id)
    except errors.PyMongoError as e:
        print(e)


