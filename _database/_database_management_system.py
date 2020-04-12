import sqlite3, time
from colorama import init, Fore, Style
from os import system

RED = Fore.RED + Style.BRIGHT
YELLOW = Fore.YELLOW + Style.BRIGHT
GREEN = Fore.GREEN + Style.BRIGHT
CYAN = Fore.CYAN + Style.BRIGHT
BLUE = Fore.BLUE + Style.BRIGHT
MAGENTA = Fore.MAGENTA + Style.BRIGHT
ALL_COLORS = [RED, YELLOW, GREEN, CYAN, BLUE, MAGENTA]

const = 0.1

class RIMZDBMS:
    
    def __init__(self, dbFile):
        self.db = self.createConnection(dbFile)
        self.latestID = 0
        
    def __del__(self):
        del self.db
        
    def createConnection(self, dbFile):
        try:
            conn = sqlite3.connect(dbFile)
        except sqlite3.Error as e:
            print("createConnection: ", e)
        return conn
    
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
    
    def createTable(self, sqlQuery):
        self.queryExecute(sqlQuery)
        
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
        
    def insertQuestion(self, questionDesc):
        if self.checkIfExists("questionDesc", "QuestionItem", args={"questionDesc":questionDesc,}):
            print("Question already exists")
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
    
    def insertChoice(self, choiceDesc, questionID):
        if self.checkIfExists("choiceDesc", "ChoiceItem", args={"choiceDesc": choiceDesc, "questionID": questionID}):
            print("Choice already exists")
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
        
    def setCorrectAnswer(self, questionID, correctChoiceID):
        queryDesc = """
                        UPDATE QuestionItem
                        SET correctChoiceID = ?
                        WHERE questionID = ?
                    """
        self.queryExecute(queryDesc, commit=True, args=(correctChoiceID, questionID))
        
    def changeChoice(self, choiceDesc, questionID, choiceID):
        queryDesc = """
                    UPDATE ChoiceItem
                    SET choiceDesc = ?
                    WHERE questionID = ?
                    AND choiceID = ?
                """
        self.queryExecute(queryDesc, commit=True, args=(choiceDesc, questionID, choiceID))
        
    def getAllFromTable(self, tableName):
        queryDesc = "SELECT * FROM {0}".format(tableName)
        return self.queryExecute(queryDesc, fetchAll=True)
    
    def deleteChoice(self, questionID, choiceID):
        queryDesc = "DELETE FROM ChoiceItem WHERE questionID = ? AND choiceID = ?"
        self.queryExecute(queryDesc, commit=True, args=(questionID, choiceID))
        
    def deleteQuestion(self, questionID):
        queryDesc = "DELETE FROM QuestionItem WHERE questionID = ?"
        self.queryExecute(queryDesc, commit=True, args=(questionID,))
        if not self.checkIfExists("questionID", "QuestionItem", args={"questionID": questionID,}):
            print("\n\t\tQuestion ID:", questionID, "is deleted.")
        queryChoiceID = "SELECT choiceID FROM ChoiceItem WHERE questionID = ?"
        choicesID = [ID[0] for ID in self.queryExecute(queryChoiceID, fetchAll=True, args=(questionID,))]
        for choiceID in choicesID:
            self.deleteChoice(questionID, choiceID)
            print("\t\tChoice ID:", choiceID, "is deleted.")
            
    def checkIDs(self, idName, tableName):
        queryDesc = "SELECT {0} FROM {1}".format(idName, tableName)
        results = [ID[0] for ID in self.queryExecute(queryDesc, fetchAll=True)]
        if len(results) == 0:
            self.resetID(tableName)
            
    def getID(self, questionDesc):
        queryDesc = "SELECT questionID FROM QuestionItem WHERE questionDesc = ?"
        ID = self.queryExecute(queryDesc, fetchOne=True, args=(questionDesc,))[0]
        return ID
    
    def resetID(self, tableName):
        queryDesc = "UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME = ?"
        self.queryExecute(queryDesc, commit=True, args=(tableName,))

    def getChoices(self, questionID):
        queryDesc = "SELECT * FROM ChoiceItem WHERE questionID = ?;"
        results = self.queryExecute(queryDesc, fetchAll=True, args=(questionID, ))
        return results
        

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

db = RIMZDBMS("_RIMZ.db")
db.createTable(create_question_table)
db.createTable(create_choice_table)

def delay(const):
    time.sleep(const)

def verifyCancel(cancel):
   if cancel != 0:
      return True
   else:
      return False

def setItem():
    db.checkIDs("questionID", "QuestionItem")
    question = input("\n\t\tInput question [Type 0 to cancel]: ")
    if question == "0": return
    if not db.insertQuestion(question):
        return
    else:
        ID = db.getID(question)
    for x in range(1, 4+1):
        choice = input("\t\tIndex [{0}] Input Choice [Type 0 to cancel]: ".format(x))
        if choice == "0":
            db.deleteQuestion(ID)
            return
        db.insertChoice(choice, ID)
    answer = int(input("\n\t\tInput correct answer (by index): "))
    db.setCorrectAnswer(ID, answer)

def showQuestions():
    questions = db.getAllFromTable("QuestionItem")
    for question in questions:
        delay(const)
        questionID = question[0]
        questionDesc = question[1]
        questionAnswer = question[2]
        choices = db.getChoices(questionID)
        print(RED, "\n\t\tquestionID:", questionID)
        delay(const)
        print(YELLOW, "\t\tQuestion Description:", questionDesc)
        delay(const)
        print(GREEN, "\t\tQuestion Answer [INDEX]: ", questionAnswer)
        delay(const)
        print(CYAN, "\n\t\tChoices:")
        for index in range(0, len(choices)):
            delay(const)
            choiceDesc = choices[index][2]
            choiceID = choices[index][0]
            print(MAGENTA, "\t\tINDEX [", index+1, "] [choiceID: ", choiceID, "]: \"", choiceDesc, "\"", sep="")

def deleteChoice():
    print(MAGENTA, "\n\t\tWhich choiceID do you want to delete?")
    showQuestions()
    print(RED)
    choiceID = int(input("\t\tDelete choice (by choiceID) [Type 0 to cancel]: "))
    if verifyCancel(choiceID) == 0: return
    db.deleteChoice(1, choiceID)

def deleteQuestion():
   print(MAGENTA, "\n\t\tWhich questionID do you want to delete?")
   showQuestions()
   print(RED)
   questionID = int(input("\t\tDelete question (by questionID) [Type 0 to cancel]: "))
   if verifyCancel(questionID) == 0: return
   db.deleteQuestion(questionID)
   db.checkIDs("choiceID", "ChoiceItem")

def changeChoice():
    print(RED, "\n\t\tWhich choiceID do you want to delete?")
    print(YELLOW)
    questionID = int(input("\t\tQuestion ID [Type 0 to cancel]: "))
    if verifyCancel(questionID) == 0: return
    choiceID = int(input("\t\tChoice ID [Type 0 to cancel]: "))
    if verifyCancel(choiceID) == 0: return
    choiceDesc = input("\t\tNew Choice Description [Type 0 to cancel]: ")
    if choiceDesc == "0": return
    db.changeChoice(choiceDesc, questionID, choiceID)

def showAll():
    delay(const)
    questions = db.getAllFromTable("QuestionItem")
    choices = db.getAllFromTable("ChoiceItem")
    i = 0
    print(GREEN, "\n\t\tQuestions")
    for index in range(0, len(questions)):
        delay(const)
        if i >= len(ALL_COLORS):
            i = 0
        print(ALL_COLORS[i], "\t\t", questions[index])
        i+=1
    print("\n\t\tChoices")
    i = 0
    for index in range(0, len(choices)):
        delay(const)
        if i >= len(ALL_COLORS):
            i = 0
        print(ALL_COLORS[i], "\t\t", choices[index])
        i+=1
        
while True:
    init(wrap=True)
    choices = ["Create Question and 4 Choices",
               "Delete Choice",
               "Delete Question",
               "Change Choice",
               "Show Questions",
               "Show All",
               "Exit"]
    print(YELLOW + "\n\tChoices: \n")
    for index in range(0, len(choices)):
        print(GREEN, "\t\t", index+1, ".) ", choices[index], sep="")
    print(CYAN)
    select = input("\tSELECT [1-{0}]: ".format(len(choices)))
    if select == "1":
        setItem()
    elif select == "2":
        deleteChoice()
    elif select == "3":
        deleteQuestion()
    elif select == "4":
        changeChoice()
    elif select == "5":
        showQuestions()
    elif select == "6":
        showAll()
    elif select == "7":
        break
    print(BLUE)
    input("\t\tPress any key to continue...")
    system("cls")
