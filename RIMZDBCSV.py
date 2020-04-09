import sqlite3, csv, os, time

const = 0.1

create_question_table = """
                            CREATE TABLE IF NOT EXISTS QuestionItem(
                                questionID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                questionDesc text NOT NULL,
                                correctChoiceID integer
                            );
                        """

create_choice_table =  """
                            CREATE TABLE IF NOT EXISTS ChoiceItem(
                                choiceID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                                questionID integer NOT NULL,
                                choiceDesc text NOT NULL,
                                FOREIGN KEY(questionID) REFERENCES QuestionItem(questionID) 
                            );
                       """

create_master_table = """
                          CREATE TABLE IF NOT EXISTS master (
                              masterID integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                              authorID text NOT NULL,
                              masterName text,
                              score real
                          );
                      """

class importItems:

    def __init__(self, dbFile):
        self.db = self.createConnection(dbFile)

    def importCSV(self, csvFile):
        self.verify = True
        self.createMasterTable()
        self.createQnATables()
        self.parseCSVFile(csvFile)
        if not self.verify:
            return
        del self.verify
        self.addQuestions()
        list(map(self.addChoices, self.choiceFields))
        self.db.commit()
        self.db.close()

    def createConnection(self, dbFile):
        try:
            conn = sqlite3.connect(dbFile)
        except sqlite3.Error as e:
            print("createConnection: ", e)
        return conn

    def createMasterTable(self):
        try:
            time.sleep(const)
            print("Created master table")
            self.db.execute(create_master_table)
        except sqlite3.Error as e:
            print("createQnATables: ", e)

    def createQnATables(self):
        try:
            self.cursor = self.db.cursor()
            self.db.execute("DROP TABLE IF EXISTS QuestionItem")
            time.sleep(const)
            print("Dropped QuestionItem table")
            self.db.execute("DROP TABLE IF EXISTS ChoiceItem")
            time.sleep(const)
            print("Dropped ChoiceItem table")
            self.cursor.execute(create_question_table)
            time.sleep(const)
            print("Created QuestionItem table")
            self.cursor.execute(create_choice_table)
            time.sleep(const)
            print("Created ChoiceItem table")
        except sqlite3.Error as e:
            print("createQnATables: ", e)

    def parseCSVFile(self, csvFile):
        if csvFile.endswith(".csv"):
            try:
                with open(csvFile, "r") as csv_file:
                    csv_reader = list(csv.reader(csv_file, delimiter=","))
                    self.questionFields = [fields[:2] for fields in csv_reader]
                    self.choiceFields = [[index+1, fields[2:]] for index, fields in enumerate(csv_reader)]
            except csv.Error as e:
                print("parseCSVFile: ", e)
        else:
            self.verify = False
            print("parseCSVFile: Invalid file type")

    def addQuestions(self):
        questionFields = self.questionFields
        self.cursor.executemany("""
                            INSERT INTO QuestionItem (
                                questionDesc,
                                correctChoiceID
                            ) VALUES (
                                ?,
                                ?
                            );
                        """, questionFields)
        time.sleep(const)
        print("questionFields added")

    def addChoices(self, choiceFields):
        for index in range(0, len(choiceFields[1])):
            questionID = choiceFields[0]
            choiceDesc = choiceFields[1][index]
            self.cursor.execute("""
                        INSERT INTO ChoiceItem (
                            questionID,
                            choiceDesc
                        ) VALUES (
                            ?,
                            ?
                        );
                    """, (questionID, choiceDesc))
            time.sleep(const)
            print("questionID: {0} added\nchoiceDesc: '{1}' added".format(questionID, choiceDesc))

if __name__=="__main__":
    os.system("color a")
    importQnA = importItems("RIMZDB.db")
    csvFileName = input("CSV Filename [ EXAMPLE '<filename.csv>' ]: ")
    importQnA.importCSV(csvFileName)
    os.system("cls")
    os.system("RIMZDBMS.py")
