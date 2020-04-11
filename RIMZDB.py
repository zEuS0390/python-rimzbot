import sqlite3

# Database Class
class RIMZDB:

    # Constructor with 1 parameter for the filename of the database
    def __init__(self, dbFile):
        self.db = self.createConnection(dbFile)
        self.qncTables()
        self.masterTable()
        
    # Destructor deletes the database
    def __del__(self):
        del self.db

    # Creates a database if it did not exist
    def createConnection(self, dbFile):
        try:
            conn = sqlite3.connect(dbFile)
        except sqlite3.Error as e:
            print("createConnection: ", e)
        return conn

    # Accepts any SQLite query with 1 parameter for a positional 
    # argument and a parameter for keyworded arguments
    def queryExecute(self, sqlQuery, **kwargs):
        commands = ("fetchOne", "fetchAll", "commit")
        arguments = self.getArguments(*commands, **kwargs)
        try:
            query = self.db.cursor()
            if len(arguments["args"]) > 0 and (arguments.get(commands[0]) is None or arguments.get(commands[1]) is None):
                query.execute(sqlQuery, arguments["args"])
            else:
                query.execute(sqlQuery)
            for key, value in arguments.items():
                if key == commands[0]:
                    return query.fetchone()
                elif key == commands[1]:
                    return query.fetchall()
                elif key == commands[2]:
                    self.db.commit()
        except sqlite3.Error as e:
            print("queryExecute: ", e)
        query.close()

    # Gets arguments through veriable-length argument lists 
    def getArguments(self, *args, **kwargs):
        values = {}
        values["args"] = ()
        for key, value in kwargs.items():
            for arg in args:
                if key == arg and value == True:
                    values[key] = value
            if key == "args" and (isinstance(value, tuple) or isinstance(value, list)):
                values["args"] = value
        return values

    # Creates table that accepts 1 parameter to define rows and columns
    def createTable(self, sqlQuery):
        self.queryExecute(sqlQuery)

    # Checks if the given argument exists in the table
    def checkIfExists(self, field, table, **kwargs):
        conditions = []
        keyValues = []
        for key, value in kwargs.items():
            if key == "args" and isinstance(value, dict):
                for k, v in value.items():
                    keyValues.append(v)
                    conditions.append("{0} = ?".format(k))
        queryDesc = "SELECT {0} FROM {1} WHERE " + " AND ".join(conditions)
        queryDesc = queryDesc.format(field, table)
        results = self.queryExecute(queryDesc, fetchOne=True, args=keyValues)
        if results is not None:
            return True
        else:
            return False

    # Creates QuestionItem and ChoiceItem tables if they don't exist
    def qncTables(self):
        QuestionItemDesc = """
                               CREATE TABLE IF NOT EXISTS QuestionItem (
                                   questionID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                   questionDesc text NOT NULL,
                                   correctChoiceID integer
                               );
                           """
        ChoiceItemDesc =  """
                              CREATE TABLE IF NOT EXISTS ChoiceItem (
                                  choiceID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                  questionID integer NOT NULL,
                                  choiceDesc text NOT NULL,
                                  FOREIGN KEY(questionID) REFERENCES QuestionItem(questionID) 
                              );
                          """
        self.createTable(QuestionItemDesc)
        self.createTable(ChoiceItemDesc)

    # Creates master table if it does not exist
    def masterTable(self):
        masterDesc = """
                         CREATE TABLE IF NOT EXISTS master (
                             masterID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                             authorID text NOT NULL,
                             masterName text,
                             score real
                         );
                     """
        self.createTable(masterDesc)

    # Inserts a question to the questionItem table
    def insertQuestion(self, questionDesc):
        if self.checkIfExists("questionDesc", "QuestionItem", args={"questionDesc":questionDesc,}):
            print("insertQuestion: Question already exists")
            return False
        queryDesc = """
                        INSERT OR REPLACE INTO QuestionItem(
                            questionDesc
                        ) VALUES (
                            ?
                        );
                    """
        self.queryExecute(queryDesc, commit=True, args=(questionDesc,))
        return True

    # Inserts a choice to choiceItem table for the question in the questionItem table
    def insertChoice(self, choiceDesc, questionID):
        if self.checkIfExists("choiceDesc", "ChoiceItem", args={"choiceDesc": choiceDesc, "questionID": questionID}):
            print("insertChoice: Choice already exists")
            return
        queryDesc = """
                        INSERT INTO ChoiceItem(
                            choiceDesc,
                            questionID
                        ) VALUES (
                            ?,
                            ?
                        );
                    """
        self.queryExecute(queryDesc, commit=True, args=(choiceDesc, questionID))

    # Sets a correct answer for a question in the questionItem table
    def setCorrectAnswer(self, questionID, correctChoiceID):
        queryDesc = """
                        UPDATE QuestionItem
                        SET correctChoiceID = ?
                        WHERE questionID = ?
                    """
        self.queryExecute(queryDesc, commit=True, args=(correctChoiceID, questionID))

    # Change the description of the choice in the choiceItem table for a question in the questionItem table
    def changeChoice(self, choiceDesc, questionID, choiceID):
        queryDesc = """
                        UPDATE ChoiceItem
                        SET choiceDesc = ?
                        WHERE questionID = ?
                        AND choiceID = ?
                    """
        self.queryExecute(queryDesc, commit=True, args=(choiceDesc, questionID, choiceID))

    # Gets all fields in the table of the database
    def getAllFromTable(self, tableName):
        queryDesc = """
                        SELECT *
                        FROM {0}
                    """.format(tableName)
        return self.queryExecute(queryDesc, fetchAll=True)

    # Deletes a choice from the choiceItem table of the question in the questionItem table
    def deleteChoice(self, questionID, choiceID):
        queryDesc = """
                        DELETE
                        FROM ChoiceItem
                        WHERE questionID = ?
                        AND choiceID = ?
                    """
        self.queryExecute(queryDesc, commit=True, args=(questionID, choiceID))

    # Deletes question in the questionItem table using questionID
    def deleteQuestion(self, questionID):
        queryDesc = """
                        DELETE
                        FROM QuestionItem
                        WHERE questionID = ?
                    """
        self.queryExecute(queryDesc, commit=True, args=(questionID,))
        print("deleteQuestion: Question ID:", questionID, "is deleted.")
        queryChoiceID = """
                            SELECT choiceID
                            FROM ChoiceItem
                            WHERE questionID = ?
                        """
        choicesID = [ID[0] for ID in self.queryExecute(queryChoiceID, fetchAll=True, args=(questionID,))]
        for choiceID in choicesID:
            self.deleteChoice(questionID, choiceID)
            print("deleteQuestion: Choice ID:", choiceID, "is deleted.")

    # Checks the sequential row ID of the autoincrement
    # IF the length of the fields in table is 0, then
    # reset the autoincrement to 1
    def checkIDs(self, idName, tableName):
        queryDesc = """
                        SELECT {0}
                        FROM {1}
                    """.format(idName, tableName)
        results = [ID[0] for ID in self.queryExecute(queryDesc, fetchAll=True)]
        if len(results) == 0:
            self.resetID(tableName)

    # Gets the questionID of the latest question
    def getID(self, questionDesc):
        queryDesc = """
                        SELECT questionID
                        FROM QuestionItem
                        WHERE questionDesc = ?
                    """
        ID = self.queryExecute(queryDesc, fetchOne=True, args=(questionDesc,))[0]
        return ID

    # Resets the autoincrement of a table
    def resetID(self, tableName):
        queryDesc = """
                        UPDATE SQLITE_SEQUENCE
                        SET SEQ=0
                        WHERE NAME = ?
                    """
        self.queryExecute(queryDesc, commit=True, args=(tableName,))
        print("resetID: reset ID")
