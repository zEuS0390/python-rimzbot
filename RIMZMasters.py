from RIMZDB import RIMZDB

deleteMaster = """
                    DROP TABLE master;
               """

queryDesc = """
                CREATE TABLE master (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        authorID integer,
                        master_name text,
                        score real
                );
            """

class master(RIMZDB):
    def __init__(self, dbFile):
        super(master, self).__init__(dbFile)
    def getMasters(self):
        queryDesc = """
                        SELECT * FROM master
                    """
        masters = self.queryExecute(queryDesc, fetchAll=True)
        return masters
    def insertMaster(self, authorID, master_name):
        if self.checkIfExists("master_name", "master", args={"authorID":authorID,}):
            print("Already exists")
            return
        queryDesc = """
                        INSERT INTO master (
                            authorID,
                            master_name
                        ) VALUES (
                            ?,
                            ?
                        );
                    """
        self.queryExecute(queryDesc, commit=True, args=(authorID, master_name))
        print("AUTHOR ID {0} AND MASTER NAME ({1}) HAS BEEN INSERTED IN THE TABLE MASTER OF THE DATABASE".format(authorID, master_name))

db = master("RIMZDB.db")
db.queryExecute(deleteMaster, commit=True)
db.queryExecute(queryDesc, commit=True)
