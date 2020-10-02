import discord
from minoshiro import *
from discord.ext import commands
from discord.utils import get
import graphene
import json
import requests

Token = "a secret"
client = discord.Client()
#history = False
pizzapoll = False
pizzas = [] #list of pizzas, should be untruncated strings in here
pizzavotes = [] #list of ints that represent individual votes
pizzavoters = [] #list of Voter objects to make sure unique voters in pizza poll
voterslist = [] #list of message.author to make sure unique voters in pizza poll
submissions = [] #list of Submission objects
submitcount = 0
hangingman = None
ishang = False
num_emotes = [":one:",":two:",":three:",":four:",":five:"
              ,":six:",":seven:",":eight:",":nine:",":ten:"]

class MyClient(discord.Client):
    async def on_ready(self):
        print("ready")
    
    async def on_message(self, message):
        global pizzapoll
        global pizzas
        global history
        global pizzamsg
        global submitcount
        global submissions
        global pizzavotes
        global pizzavoters
        global voterslist
        global ishang
        global hangingman
        if message.author == client.user:
            #if history:
                #count = 0
                #while count < len(num_emotes):
                    #if num_emotes[count] in pizzamsg:
                        #react=str(count+1)+"\u20e3"
                        #await message.add_reaction(react)
                    #count+=1
                #history = False
            #else:
            return
        
        channel_general = client.get_channel(723734556343140413) #restricted channel
        channel_other = channel_general
    
        if isinstance(message.channel, discord.DMChannel):
            if message.content.startswith("!hangman") and ishang == False: #hangman functions
                if message.content.endswith("!hangman"):
                    await message.author.send("Enter a word to begin a new hangman with")
                    msg = await client.wait_for('message', check=check(message.author))
                    theword = str(msg.content).replace(" ","")
                    await message.author.send("Begin a new hangman with word " + theword + "? Confirm by typing yes or no")
                else:
                    theword = str(message.content)[8:].replace(" ","")
                    await message.author.send("Begin a new hangman with word " + theword + "? Confirm by typing yes or no")
                msges = await client.wait_for('message', check=check(message.author))
                themsg = msges.content.lower()
                while "yes" not in themsg or "no" not in themsg:
                    if "yes" in themsg:
                        themsg += "no"
                    if "no" in themsg:
                        themsg += "yes"
                    else: 
                        mess = await client.wait_for('message', check=check(message.author))
                        themsg = mess.content.lower()
                if themsg.endswith("no") or themsg.startswith("yes"):
                    tempword = ""
                    for i in range(len(theword)):
                        tempword += "\_ "
                    ishang = True
                    hangingman = Hangman(message.author.name, theword)
                    await channel_other.send(message.author.mention + " has started a new hangman")
                    embed = discord.Embed(title = message.author.name + "'s hangman")
                    embed.add_field(name = "\u200b ", value = " ! ", inline = True)
                    embed.add_field(name = "Guess the word", value = tempword, inline = True)
                    await channel_other.send(embed = embed)
                else:
                    await message.author.send("Canceling hangman, type !hangman to start over")
            if message.content.startswith("!hangman") and ishang == True:
                await message.author.send("Wait your turn, there is an active hangman going on") 
            
            if message.content.startswith("!new"): #cube functions
                newsub = Submission()
                await message.author.send("Enter your submission")
                msg = await client.wait_for('message', check=check(message.author))
                while msg.content != "!stop" and msg.content != "!new":
                    if not msg.attachments:
                        newsub.addcontent(msg.content)
                    else:
                        urlstart = str(msg.attachments).index("url=")+5
                        slice = str(msg.attachments)[urlstart:-3]
                        slice = str(msg.content)+"\t"+slice
                        newsub.addcontent(slice)
                    msg = await client.wait_for('message', check=check(message.author))
                if len(newsub.getcontent()) > 0:
                    submitcount += 1
                    newsub.givetag(submitcount)
                    submissions.append(newsub)
                    sendit = ""
                    subnotif = "Submission " + str(submitcount)
                    embed = discord.Embed(title = subnotif)
                    for i in range(len(newsub.getcontent())):
                        embed.add_field(name = "\u200b", value = (newsub.getcontent())[i], inline = False)
                    await channel_general.send(embed = embed)
                    
        if message.content.startswith("!EmptyCube"): #reset submission counting, will not delete past messages
            if discord.utils.get(message.author.roles, name="admin") is not None:
                submissions = []
                submitcount = 0
                
        if message.content.startswith("!guess"): #for hangman, a lot of space is taken up by the embed stuff, so it's messy
            if not ishang:
                await message.channel.send("DM the bot with !hangman first to start a new hangman")
            elif message.content.endswith("!guess"): 
                await message.channel.send(message.author.mention + "You can't guess nothing at all")
            else:
                letter = str(message.content)[6:]
                lwrcs = letter.lower()
                ltr = lwrcs.replace(" ","")
                if not hangingman.checkForDup(ltr):
                    if len(ltr) > 1:
                        if ltr == hangingman.getWord():
                            hangingman.solveit()
                            ishang = False
                            await message.channel.send(message.author.mention + " has solved the hangman!")
                            tempword1 = ""
                            tempword2 = "\u200b "
                            index1 = list(hangingman.getWord())
                            index2 = hangingman.getFails()
                            for i in range(len(index1)):
                                tempword1 = tempword1 + index1[i] + " "
                            for j in range(len(index2)):
                                tempword2 = tempword2 + index2[j] + "\n"
                            print(tempword2)
                            embed = discord.Embed(title = message.author.name + "'s hangman")
                            embed.add_field(name = "\u200b ", value = " ! ", inline = True)
                            embed.add_field(name = "Guess the word", value = tempword1, inline = True)
                            embed.add_field(name = "Guesses", value = tempword2, inline = True)
                            await message.channel.send(embed = embed)
                        else:
                            hangingman.addguess(True, ltr)
                            tempword1 = "\u200b "
                            tempword2 = "\u200b "
                            index1 = hangingman.getIndex()
                            index2 = hangingman.getFails()
                            for i in range(len(index1)):
                                tempword1 = tempword1 + index1[i] + " "
                            for j in range(len(index2)):
                                tempword2 = tempword2 + index2[j] + "\n"
                            embed = discord.Embed(title = message.author.name + "'s hangman")
                            embed.add_field(name = "\u200b ", value = " ! ", inline = True)
                            embed.add_field(name = "Guess the word", value = tempword1, inline = True)
                            embed.add_field(name = "Guesses", value = tempword2, inline = True)
                            await message.channel.send(embed = embed)
                    else:
                        if hangingman.findletter(ltr):
                            if hangingman.getIndex() == list(hangingman.getWord()):
                                hangingman.solveit()
                                ishang = False
                                await message.channel.send(message.author.mention + " has solved the hangman!")
                            tempword1 = "\u200b "
                            tempword2 = "\u200b "
                            index1 = hangingman.getIndex()
                            index2 = hangingman.getFails()
                            for i in range(len(index1)):
                                tempword1 = tempword1 + index1[i] + " "
                            print(tempword1)
                            for j in range(len(index2)):
                                tempword2 = tempword2 + index2[j] + "\n"
                            embed = discord.Embed(title = message.author.name + "'s hangman")
                            embed.add_field(name = "\u200b ", value = " ! ", inline = True)
                            embed.add_field(name = "Guess the word", value = tempword1, inline = True)
                            embed.add_field(name = "Guesses", value = tempword2, inline = True)
                            await message.channel.send(embed = embed)
                        else:
                            hangingman.addguess(True, ltr)
                            tempword1 = "\u200b "
                            tempword2 = "\u200b "
                            index1 = hangingman.getIndex()
                            index2 = hangingman.getFails()
                            for i in range(len(index1)):
                                tempword1 = tempword1 + index1[i] + " "
                            for j in range(len(index2)):
                                tempword2 = tempword2 + index2[j] + "\n"
                            embed = discord.Embed(title = message.author.name + "'s hangman")
                            embed.add_field(name = "\u200b ", value = " ! ", inline = True)
                            embed.add_field(name = "Guess the word", value = tempword1, inline = True)
                            embed.add_field(name = "Guesses", value = tempword2, inline = True)
                            await message.channel.send(embed = embed)
                else:
                    await message.channel.send(message.author.mention + ltr + " has already been guessed")

        if message.content.startswith("!pizzapoll"): #pizzapoll functions, type !pizzapoll to start and end polls
            if "display" in message.content: #type !pizzapoll display to show the current pizzas and the votes
                displayed = str(displayPizzas())
                embed = discord.Embed(title = "Current pizzas")
                embed.add_field(name = "\u200b", value = displayed)
                await message.channel.send(embed = embed)
            if message.content.endswith("!pizzapoll"): 
                if pizzapoll is False:
                    pizzapoll = not pizzapoll
                    pizzas = []
                    await message.channel.send("New pizzapoll has started!")
                elif len(pizzas) < 1:
                    pizzapoll = False
                    await message.channel.send("Pizzapoll canceled")
                else:
                    displayed = str(displayPizzas())
                    embed = discord.Embed(title = "Current pizzapoll has ended")
                    embed.add_field(name = "\u200b", value = displayed)
                    pizzapoll = not pizzapoll
                    #history = True
                    await message.channel.send(embed = embed)
                
        if message.content.startswith("!addpizza"): #adding pizza to poll, type !addpizza "pizza name" to add
            if not pizzapoll:
                await message.channel.send("Type !pizzapoll first to start a new pizza poll")
            elif message.content.endswith("!addpizza"): #if you only type !addpizza, will remind you to type name of pizza
                await message.channel.send(message.author.mention + " Name some pizzas to add to the poll")
            else:
                thepizza = str(message.content)[9:]
                pizzas.append(thepizza)
                pizzavotes.append(0)
                
        if message.content.startswith("!vote"): #voting on pizzas
            newvoter = None
            if message.author not in voterslist: #makes sure unique voters
                newvoter = Voter(message.author)
                pizzavoters.append(newvoter)
                voterslist.append(message.author)
            else:
                for i in pizzavoters:
                    if i.getAuthor() == message.author:
                        newvoter = i
            
            apizza = str(message.content)[5:]
            thepizzas = list(apizza.split(",")) #get individual pizzas
            temppizzas = []
            if message.content.endswith("!vote"):
                await message.channel.send(message.author.mention + "You can't vote for nothing at all")
            else:
                for i in pizzas: #truncate the existing pizzas
                    temppizza = i.replace(" ","") 
                    temppizzas.append(temppizza)
                for i in thepizzas:
                    actpizza = i.replace(" ","") #truncate the voted pizzas
                    if actpizza in newvoter.getVotes():
                        await message.channel.send(message.author.mention + " You already voted for this pizza")
                    elif actpizza in temppizzas: #track votes for both the poll and each user, truncated to make sure no weird stuff happens
                        index = temppizzas.index(actpizza)
                        pizzavotes[index] += 1
                        newvoter.addVotes(actpizza)
                    else:
                        await message.channel.send(message.author.mention + " Your pizza " + i + " isn't part of the poll yet,"
                                              + " use !addpizza \"insert pizza name\" to it to the poll")

            #sqlite_path = r"c:\Users\18329\Documents\Robo.db"
            #robo = await Minoshiro.from_sqlite(sqlite_path) 
            #sites = [Site.ANILIST]
            #dat = ""
            #async for data in robo.yield_data(testcase, Medium.ANIME, sites):
                #dat = str(data[1])
            #i = dat.find(":")+1
            #j = dat.find(",")
            #d = dat[i:j]

        if message.content.startswith("!animedawe fiajfoajefoajfoajfoiaj"):
            testcase = str(message.content)[7:]
            query = "{Media(search:\"" + testcase + "\"){genres}}"
            url = "https://graphql.anilist.co"
            r = requests.post(url, json={"query": query})
            await channel_general.send(r.text)
            if "Hentai" in r.text:
                await channel_general.send("no 18+ allowed")
            else:
                await channel_general.send("not 18+")

        if message.content.startswith("!character"):
            testcase = str(message.content)[10:]
            query = "{Character(search:\"" + testcase + "\"){siteUrl}}"
            url = "https://graphql.anilist.co"
            r = requests.post(url, json={"query": query})
            await message.channel.send(r.text)

        if message.content.startswith("!animesearch"):
            testcase = str(message.content)[12:]
            query = "{Media(search:\"" + testcase + "\"){siteUrl}}"
            url = "https://graphql.anilist.co"
            r = requests.post(url, json={"query": query})
            ret = str(r.text)[28:]
            retu = ret.replace("}","")
            retun = retu.replace("\"","")
            embed = discord.Embed(title = retun, url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            #"["+retun+"](https://www.youtube.com/watch?v=dQw4w9WgXcQ)"
            await message.channel.send(embed = embed)

class Hangman(): #hangman stuff
    def __init__(self, owner, word):
        self.owner = owner
        self.word = word
        self.index = []
        for i in range(len(word)):
            self.index.append("\_ ")
        self.fails = []
        self.guesses = []
        self.solved = False
    def isSolved(self):
        return self.solved
    def solveit(self):
        self.solved = True
    def findletter(self, letter):
        isThere = False
        ind = []
        for i in range(len(self.word)):
            if letter == (self.word)[i]:
                ind.append(letter)
            else:
                ind.append("\_ ")
        for i in range(len(self.index)):
            if self.index[i] != ind[i] and self.index[i] == "\_ ":
                self.index[i] = ind[i]
                isThere = True
        print(self.index)
        return isThere
    def getIndex(self):
        return self.index
    def getFails(self):
        return self.fails
    def checkForDup(self, string):
        if string in self.guesses:
            return True
        else:
            return False
    def addguess(self, failed, guess):
        self.guesses.append(guess)
        if failed:
            self.fails.append(guess)
    def getWord(self):
        return self.word
    def getOwner(self):
        return self.owner
    
def displayPizzas(): #shows pizzas + votes
    count = 0
    msg = ""
    global pizzas
    global num_emotes
    global pizzavotes
    if not pizzas:
        msg = "There are no pizzas added"
    else:
        for i in pizzas:
            msg = msg + num_emotes[count] + " " + i + " (" + str(pizzavotes[count]) + " votes), "
            count += 1
    return msg

class Voter():
    def __init__(self, author): #votes should be truncated strings
        self.author = author
        self.votes = []
    def getAuthor(self):
        return self.author
    def getVotes(self):
        return self.votes
    def addVotes(self, vote):
        self.votes.append(vote)

def check(author): #used for the wait_for() function
    def inner_check(message):
        return message.author == author
    return inner_check

class Submission(): #content should be string
    def __init__ (self):
        self.content = []
        self.tag = 0
    def addcontent(self, message):
        self.content.append(message)
    def givetag(self, tag):
        self.tag = tag
    def getcontent(self):
        return self.content
    def gettag(self):
        return self.tag
        
client = MyClient()

client.run(TOKEN)
