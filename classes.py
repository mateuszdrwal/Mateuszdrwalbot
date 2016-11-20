import time,random
from utilityFunctions import utilityFunctions
from datetime import datetime

uf = utilityFunctions()

class info: #the class for setable custom commands

    def set(self,ops,username,message):#returns chat message, imput array of users that can change the text, their username and a string containing the potential new text
        if uf.isOp(ops,username):
            self.info = message.capitalize()
            return "info successfully set to " + self.info

class timer: #speedrun timer class

    def __init__(self):
        self.active = False
        self.started = 0
    
    def start(self,title,ss3,ss3val): #start the timer
        self.started = time.time()
        ss3.update_acell("A"+str(uf.length(ss3val,0)+1),str(uf.nyctime()))
        ss3.update_acell("B"+str(uf.length(ss3val,1)+1),title)
        if self.active:
            self.active = True
            return "timer restarted for speedrun \"%s\"" % title
        else:
            self.active = True
            return "timer started for speedrun \"%s\"" % title
            
    def stop(self,message,ss3,ss3val): #stop the timer
        if self.active:
            timerTime = uf.readableTime(time.time() - self.started)
            ss3.update_acell("v"+str(uf.length(ss3val,0)),timerTime)
            ss3.update_acell("W"+str(uf.length(ss3val,0)),message)
            self.active = False
            return "timer stopped at %s with reason \"%s\"" % (timerTime,message)
        else:
            return "timer is not active"

    def status(self): #return the count of the timer
        if self.active:
            return "the timer is now at " + uf.readableTime(time.time() - self.started)
        else:
            return "timer is not active"
        
    def add(self,amount): #add x seconds to timer
        if self.active:
            try:
                self.started -= int(amount)
                return "added "+str(int(amount))+" seconds to the timer"
            except ValueError:
                return "That is not a valid integer!"
        else:
            return "timer is not active"
    
    def remove(self,amount): #remove x seconds from timer
        if self.active:
            try:
                self.started += int(amount)
                return "removed "+str(int(amount))+" seconds from the timer"
            except ValueError:
                return "That is not a valid integer!"
        else:
            return "timer is not active"
    
    def split(self,split,ss3,ss3val):#create a split if the input split is valid
        #the array of valid splits. format:
        #splits = [
        #[["s1","split1"],"A"]
        #[["s2","split2","sp2"],"B"]
        #each entry consists of 2 items, an array and a string with a char
        #the array consists of the keywords that identify that split
        #the char is the column on the spreadsheet that split should be assigned to
        #as ss3 input the gspread object of the sheet, and as ss3val the ss3.get_all_values()
        #so split("sp2",ss,ss.get_all_values) assuming ss is the gspread object would post the time in column B as sp2 is a keyword of the second split and the second splits column is B
        splits = [
            [["ks","king slime"],"C"],
            [["eoc","eye of cthulhu"],"D"],
            [["eow","boc","eater of worlds","brain of cthulhu"],"E"],
            [["qb","queen bee"],"F"],
            [["s","skeletron"],"G"],
            [["wof","wall of flesh","hardmode"],"H"],
            [["td","d","the destroyer","destroyer"],"I"],
            [["sp","skeletron prime"],"J"],
            [["tt","t","the twins","twins"],"K"],
            [["p","plantera"],"L"],
            [["g","golem"],"M"],
            [["df","duke fishron"],"N"],
            [["lc","lunatic cultist"],"O"],
            [["ml","moon lord"],"P"],
            [["gi","ga","goblin invasion","goblin army"],"Q"],
            [["pi","pirate invasion"],"R"],
            [["mm","martian madness"],"S"],
            [["ne","nights edge","night's edge"],"T"],
            [["tb","terra blade"],"U"]]
        if self.active:
            if uf.isSplit(splits,split) != "":
                timerTime = uf.readableTime(time.time() - self.started)
                ss3.update_acell(uf.isSplit(splits,split)+str(uf.length(ss3val,0)),timerTime)
                return "split %s has been created" % split
            else:
                return "I do not recognize that split and thus cannot create it"
        else:
            return "timer is not active"

class randomMessages():

    def __init__(self):
        self.array = []

    def load(self, array):
        self.array = array

    def add(self, string):
        self.array.append(string)

    def get(self):
        return self.array[random.randint(0,len(self.array)-1)]
