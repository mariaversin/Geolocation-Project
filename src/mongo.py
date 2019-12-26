from pymongo import MongoClient

client = MongoClient()

def connectCollection(database, collection):
    ''' return collection from db crunchbase'''
    db = client[database]
    coll = db[collection]
    return db, coll

