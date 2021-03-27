from sqlitedict import SqliteDict

class Database():
    def __init__(self,path):
        self.path = path
        self.authors = SqliteDict(path + '/authors.db', autocommit=True)
        self.papers =  SqliteDict(path + '/papers.db', autocommit=True)
        self.cocite =  SqliteDict(path + '/cocite.db', autocommit=True)