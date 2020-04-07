from fbchat import Client
from fbchat.models import Message, ThreadType
from getpass import getpass
from RIMZTrivia import trivia as tr
from RIMZMasters import master as m
from RIMZWebScraping import getLatestArticles
from gtts import gTTS
from vlc import Instance
from os import system, remove
from uuid import uuid4
import sympy, winsound, time
from threading import Thread
    
"""
        KEY: EM3RWHzo3IEcqVIvnjLxtV0SfsBxtdsOyaf0afVsCUo=
        CREATED BY: ZEUS JAMES S. BALTAZAR
        DATE CREATED: MARCH 31, 2020; WEDNESDAY
        DESCRIPTION: THIS IS A CHAT BOT FOR FACEBOOK MESSENGER
        EXTERNAL PREREQUISITES OF THE PROGRAM:
        ~ fbchat (pip install fbchat)
        ~ sympy (pip install sympy)
        ~ vlc   (pip install python-vlc)
        ~ gtts  (pip install gTTS)
        ~ bs4   (pip install bs4)  
"""

# Declaration of constants and instances
THREADID = "3241873795826525"
THREADTYPE = ThreadType.GROUP
commands = ["!commands",
            "!math <expression>",
            "!setname <name>",
            "!name",
            "!trivia",
            "!answer <answer>",
            "!quittrivia",
            "!latestnews",
            "!speak <message>",
            "!exit"]
trivia = tr("RIMZDB.db")
master = m("RIMZDB.db")

# Main class of the chat bot
class RIMZBot(Client):

    # A method to send a message to a given threadID
    def sendMessage(self, message_text):
        self.send(Message(text="{0}".format(message_text)), thread_id=THREADID, thread_type=THREADTYPE)

    # Validates a message to execute a specific command
    def validateMessage(self, command, message):
        if message.text is not None and message.text.startswith(command):
            return True
        else:
            return False

    # Validates expression for the mathExpression method
    def validateExpression(self, sympyEq):
        try:
            str(float(sympy.sympify(sympyEq)))
            return True
        except:
            return False

    # Parses message
    def fetchMessage(self, message):
        return " ".join(message.text.split()[1:])

    # A method for math command
    def mathExpression(self, message):
        mathArith = self.fetchMessage(message)
        answer = sympy.sympify(mathArith)
        if self.validateExpression(answer):
            self.sendMessage(mathArith + " = " + str(float(sympy.sympify(mathArith))))
        else:
            self.sendMessage("Insert valid expression!")

    # Sets or changes the master name of the user
    def setName(self, message):
        if len(message.text.split()) > 1:
            name = self.fetchMessage(message)
            master.insertMasterName(self.authorID, name)
            self.sendMessage("Okay, I'll call you as {0}".format(name))
        else:
            self.sendMessage("Insert name!")

    # Verifies the user if it already has a master name or not
    def verifyName(self):
        if self.authorID in master.getAuthorIDs():
            return master.getMasterName(self.authorID)
        else:
            name = self.fetchUserInfo(self.authorID)[self.authorID].name
            master.insertMasterName(self.authorID, name)
            return name

    # Gets the master name of the user from the database
    def masterName(self, message):
        if self.authorID in master.getAuthorIDs():
            self.sendMessage(master.getMasterName(self.authorID))
        else:
            self.sendMessage("You don't have master name")

    # Initiates trivia game
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

    # Answers the trivia question
    def answerTrivia(self, message):
        answer = self.fetchMessage(message)
        messenger = self.verifyName()
        if trivia.checkAnswer(answer):
            points = master.getScore(self.authorID)
            master.insertScore(self.authorID, 1)
            self.sendMessage("Points: {0} + 1.0\n{1}'s answer is correct!".format(points, messenger))
        else:
            points = master.getScore(self.authorID)
            master.insertScore(self.authorID, -1)
            self.sendMessage("Points: {0} - 1.0\n{0}'s answer is wrong! The correct answer is {1}.".format(points, messenger, trivia.getCorrectAnswer()))
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
            points = master.getScore(self.authorID)
            self.sendMessage("Points: {0}\nTrivia game has ended. Type !trivia to play again.".format(points))

    # Quits the trivia game if it is running
    def quitTrivia(self):
        messenger = self.verifyName()
        if trivia.flag == True:
            trivia.flag = False
            trivia.resetNumber()
            self.sendMessage("{0} cancelled the trivia game".format(messenger))
        else:
            self.sendMessage("Trivia game has not been started yet.")

    # Display commands of the bot
    def displayCommands(self):
        text = "Commands:\n"
        for index in range(0, len(commands)):
            text += "{0}. ".format(index+1) + commands[index]
            if index < len(commands)-1:
                text += "\n"
        self.sendMessage(text)

    # Play sound until it stops
    def playSound(self, soundFile):
        vlc_instance = Instance()
        player = vlc_instance.media_player_new()
        media = vlc_instance.media_new(soundFile)
        player.set_media(media)
        player.play()
        time.sleep(1.5)
        duration = player.get_length() / 1000
        time.sleep(duration)

    # A method that plays a speech generated by the gTTS API
    def playSpeech(self, message, sendVoiceClip=False):
        filename = uuid4().hex + ".mp3"
        name = self.fetchUserInfo(self.authorID)[self.authorID].name
        message = self.fetchMessage(message)
        speech = "Message from {0}. {1}".format(name, message)
        textToSpeech = gTTS(text=speech, lang="en-us")
        textToSpeech.save(filename)
        for times in range(0, 4):
            winsound.Beep(1500, 300)
        self.playSound(filename)
        if sendVoiceClip:
            self.sendLocalVoiceClips(filename, thread_id=THREADID, thread_type=THREADTYPE)
        remove(filename)

    # A method to gather news article headlines from a news website (ABS-CBN)
    def latestNews(self):
        latestArticles = getLatestArticles(5)
        articleTimes = list(latestArticles.keys())
        message = "Here's the latest news from the ABS-CBN:\n"
        for index in range(0, len(latestArticles)):
            articleTime = articleTimes[index]
            article = latestArticles[articleTime]
            message += "{0}.) ".format(index+1) + article + " [" + articleTime + "]\n"
        self.sendMessage(message)

    # A method called when the client is listening and aomebody sends a message
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
        self.authorID = author_id
        message = message_object
        if thread_id == THREADID and self.authorID == self.uid:
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
            elif "!latestnews" == message.text:
                self.latestNews()
            elif self.validateMessage("!speak", message):
                thread = Thread(target=self.playSpeech, args=(message, True))
                thread.start()
            elif "!commands" == message.text:
                self.displayCommands()
            elif "!exit" == message.text:
                self.sendMessage("RIMZBot is now offline.")
                self.stopListening()
                self.logout()
            else:
                thread = Thread(target=self.playSpeech, args=(message,))
                thread.start()
            self.markAsDelivered(THREADID, message.uid)
            self.markAsRead(THREADID)

if __name__=="__main__":
    system("color a")
    email = input("Email Address: ")
    password = getpass()
    client = RIMZBot(email, password)
    client.sendMessage("RIMZBot is now online.")
    client.listen()
