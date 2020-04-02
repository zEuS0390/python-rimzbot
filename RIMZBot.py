from fbchat import Client
from fbchat.models import Message, ThreadType
from getpass import getpass
from itertools import product
import sympy
from RIMZTrivia import trivia as tr

"""
        CREATED BY: ZEUS JAMES S. BALTAZAR
        DATE CREATED: MARCH 31, 2020; WEDNESDAY
        DESCRIPTION: THIS IS A CHAT BOT FOR FACEBOOK MESSENGER
"""

masters = {}
##THREADID = "3241873795826525"  # RIMZ Thread (FB)
##THREADTYPE = ThreadType.GROUP
THREADID = "100037949887123"
THREADTYPE = ThreadType.USER
commands = ["!commands",
            "!math <expression>",
            "!setname <name>",
            "!name",
            "!trivia",
            "!answer <answer>",
            "!quittrivia",
            "!exit"]

trivia = tr("RIMZDB.db")

class RIMZBot(Client):

    def sendMessage(self, message_text):
        self.send(Message(text="{0}".format(message_text)), thread_id=THREADID, thread_type=THREADTYPE)
    
    def validateMessage(self, command, message):
        if message.text is not None and message.text.startswith(command):
            return True
        else:
            return False

    def validateExpression(self, sympyEq):
        try:
            str(float(sympy.sympify(sympyEq)))
            return True
        except:
            return False

    def fetchMessage(self, message):
        return " ".join(message.text.split()[1:])

    def mathExpression(self, message):
        mathArith = self.fetchMessage(message)
        answer = sympy.sympify(mathArith)
        if self.validateExpression(answer):
            self.sendMessage(mathArith + " = " + str(float(sympy.sympify(mathArith))))
        else:
            self.sendMessage("Insert valid expression!")

    def setName(self, message):
        if len(message.text.split()) > 1:
            name = self.fetchMessage(message)
            masters[self.authorID] = name
            self.sendMessage("Okay, I'll call you as {0}".format(name))
        else:
            self.sendMessage("Insert name!")

    def verifyName(self):
        if self.authorID in masters:
            return masters[self.authorID]
        else:
            return self.fetchUserInfo(self.authorID)[self.authorID].name

    def masterName(self, message):
        if self.authorID in masters:
            self.sendMessage(masters[self.authorID])
        else:
            self.sendMessage("You don't have master name")

    def startTrivia(self):
        if trivia.flag == False:
            self.sendMessage("Let's get started!")
            trivia.flag = True
            trivia.getItems()
            trivia.getQuestionItem()
            questionDesc = "{0}. ".format(trivia.itemNumber) + trivia.getQuestionDesc()
            self.sendMessage(questionDesc)
            choices = trivia.getChoices()
            string = ""
            for index in range(0, len(choices)):
                key = list(choices.keys())[index]
                keyDesc = choices[key]
                string += "{0}. {1}".format(key, keyDesc)
                if index != len(choices)-1:
                    string+= "\n"
            self.sendMessage(string)
        else:
            self.sendMessage("Trivia game has already been started.")

    def answerTrivia(self, message):
        answer = self.fetchMessage(message)
        messenger = self.verifyName()
        if trivia.checkAnswer(answer):
            self.sendMessage("{0}'s answer is correct!".format(messenger))
        else:
            self.sendMessage("{0}'s answer is wrong! The correct answer is {1}.".format(messenger, trivia.getCorrectAnswer()))
        trivia.itemNumber += 1
        trivia.removeQuestionItem()

        if trivia.questionItemLength() > 0:
            trivia.getQuestionItem()
            questionDesc = "{0}. ".format(trivia.itemNumber) + trivia.getQuestionDesc()
            self.sendMessage(questionDesc)
            choices = trivia.getChoices()
            string = ""
            for index in range(0, len(choices)):
                key = list(choices.keys())[index]
                keyDesc = choices[key]
                string += "{0}. {1}".format(key, keyDesc)
                if index != len(choices)-1:
                    string+= "\n"
            self.sendMessage(string)
        else:
            trivia.flag = False
            trivia.resetNumber()
            self.sendMessage("Trivia game has ended. Type !trivia to play again.")

    def quitTrivia(self):
        messenger = self.verifyName()
        if trivia.flag == True:
            trivia.flag = False
            trivia.resetNumber()
            self.sendMessage("{0} cancelled the trivia game".format(messenger))
        else:
            self.sendMessage("Trivia game has not been started yet.")

    def displayCommands(self):
        text = "Commands:\n"
        for index in range(0, len(commands)):
            text += "{0}. ".format(index+1) + commands[index]
            if index < len(commands)-1:
                text += "\n"
        self.sendMessage(text)

    def getCombinations(self, message):
        string = self.fetchMessage(message)
        self.sendMessage("\n".join(stringComb.getStringCombinations(string)))
        
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):

        self.authorID = author_id
        message = message_object
        
        if thread_id == THREADID:
            if self.validateMessage("!math", message):
                self.mathExpression(message)
            elif self.validateMessage("!combinations", message):
                self.getCombinations(message)
            elif self.validateMessage("!setname", message):
                self.setName(message)
            elif "!name" == message.text:
                self.masterName(message)
            elif "!trivia" == message.text:
                self.startTrivia()
            elif self.validateMessage("!answer", message):
                self.answerTrivia(message)
            elif "!quittrivia" == message.text:
                self.quitTrivia()
            elif "!commands" == message.text:
                self.displayCommands()
            elif "!exit" == message.text:
                self.sendMessage("RIMZBot is now offline.")
                self.stopListening()
            self.markAsDelivered(THREADID, message.uid)
            self.markAsRead(THREADID)

if __name__=="__main__":
    email = "ares.eureka"
    password = getpass()
    client = RIMZBot(email, password)
    client.sendMessage("RIMZBot is now online.")
    client.listen()
