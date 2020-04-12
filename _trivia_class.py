from _database._database_class import RIMZDB
from random import choice

questionTableName = "QuestionItem"
choiceTableName = "ChoiceItem"

class trivia(RIMZDB):
    
    def __init__(self, dbFile):
        super(trivia, self).__init__(dbFile)
        self.flag = False
        self.itemNumber = 1
        
    def getItems(self):
        self.questionItems = {}
        questions = self.getAllFromTable(questionTableName)
        choices = self.getAllFromTable(choiceTableName)
        try:
            for question in questions:
                temp = []
                for choice in choices:
                    if question[0] == choice[1]:
                        temp.append(choice[2])
                        self.questionItems[question[0]] = (question[1], temp, question[2])
        except TypeError:
            return

    def questionItemLength(self):
        return len(self.questionItems)

    def removeQuestionItem(self):
        del self.questionItems[self.qID]
        
    def resetNumber(self):
        self.itemNumber = 1

    def getQuestionItem(self):
        questionItems = list(self.questionItems.keys())
        self.qID = choice(questionItems)

    def getQuestionDesc(self):
        return self.questionItems[self.qID][0]

    def getChoices(self):
        letter = ["A", "B", "C", "D"]
        choices = {}
        for index in range(0, len(letter)):
            choices[letter[index]] = self.questionItems[self.qID][1][index]
        return choices

    def getCorrectAnswer(self):
        correctAnswer = self.questionItems[self.qID][2]
        return self.convertIndexToLetter(correctAnswer)

    def convertLetterToIndex(self, letter):
        if letter in ["A", "a"]:
            return 1
        elif letter in ["B", "b"]:
            return 2
        elif letter in ["C", "c"]:
            return 3
        elif letter in ["D", "d"]:
            return 4

    def convertIndexToLetter(self, index):
        if index == 1:
            return "A"
        elif index == 2:
            return "B"
        elif index == 3:
            return "C"
        elif index == 4:
            return "D"

    def checkAnswer(self, answer):
        correctAnswer = self.questionItems[self.qID][2]
        if self.convertLetterToIndex(answer) == correctAnswer:
            return True
        else:
            return False
