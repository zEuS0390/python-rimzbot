from RIMZDB import RIMZDB

# Class master, inherits from RIMZDB class
class master(RIMZDB):

    # class constructor, dbFile as a path for the db file
    def __init__(self, dbFile):
        super(master, self).__init__(dbFile)

    # Gets all master from the table
    def getMasters(self):
        queryDesc = """
                        SELECT * FROM master
                    """
        masters = self.queryExecute(queryDesc, fetchAll=True)
        return masters

    # Updates master name of a specified master through authorID
    def updateMasterName(self, authorID, masterName):
        queryDesc = """
                        UPDATE master
                        SET masterName = ?
                        WHERE authorID = ?;
                    """
        self.queryExecute(queryDesc, commit=True, args=(masterName, authorID))

    # Inserts master into the table, otherwise change the master name
    def insertMasterName(self, authorID, masterName):
        queryDesc = """
                            INSERT INTO master (
                                authorID,
                                masterName,
                                score
                            ) VALUES (
                                ?,
                                ?,
                                0
                            );
                        """
        if not self.checkIfExists("masterName", "master", args={"authorID":authorID,}):
            self.queryExecute(queryDesc, commit=True, args=(authorID, masterName))
        else:
            self.updateMasterName(authorID, masterName)

    # Updates score
    def insertScore(self, authorID, score):
        queryDesc = """
                        UPDATE master
                        SET score = score + ?
                        WHERE authorID = ?;
                    """
        self.queryExecute(queryDesc, commit=True, args=(score, authorID))

    # Gets the authorID of all masters in the table
    def getAuthorIDs(self):
        queryDesc = """
                    SELECT authorID
                    FROM master
                    """
        authorIDs = self.queryExecute(queryDesc, fetchAll=True)
        authorIDs = [authorID[0] for index, authorID in enumerate(authorIDs)]
        return authorIDs

    # Gets the master name of the specified master through authorID
    def getMasterName(self, authorID):
        queryDesc = """
                    SELECT masterName
                    FROM master
                    WHERE authorID = ?;
                """
        return self.queryExecute(queryDesc, fetchOne=True, args=(authorID,))[0]

    # Gets the score of the specified master through authorID
    def getScore(self, authorID):
        queryDesc = """
                        SELECT score
                        FROM master
                        WHERE authorID = ?;
                    """
        return self.queryExecute(queryDesc, fetchOne=True, args=(authorID,))[0]

    # Resets the score of the specified master to zero through authorID
    def resetScore(self, authorID):
        queryDesc = """
                        UPDATE master
                        SET score = 0
                        WHERE authorID = ?;
                    """
        self.queryExecute(queryDesc, commit=True, args=(authorID,))
