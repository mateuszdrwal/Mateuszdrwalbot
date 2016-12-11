import time,random
from utilityFunctions import utilityFunctions
from datetime import datetime

uf = utilityFunctions()

class info: #the class for setable custom commands

    def set(self,ops,username,message):#returns chat message, imput array of users that can change the text, their username and a string containing the potential new text
        if uf.perm(ops,username,1):
            self.info = message.capitalize()
            return "info successfully set to \"%s\"" % self.info
        return "You do not have permission to do that!"

class timer: #speedrun timer class

    def __init__(self):
        self.active = False
        self.started = 0
    
    def start(self,title,ss3,ss3val): #start the timer
        self.started = time.time()
        uf.updateCell(ss3, "A"+str(uf.length(ss3val,0)+1),str(uf.nyctime()))
        uf.updateCell(ss3, "B"+str(uf.length(ss3val,1)+1),title)
        if self.active:
            self.active = True
            return "timer restarted for speedrun \"%s\"" % title
        else:
            self.active = True
            return "timer started for speedrun \"%s\"" % title
            
    def stop(self,message,ss3,ss3val): #stop the timer
        if self.active:
            timerTime = uf.readableTime(time.time() - self.started)
            uf.updateCell(ss3, "v"+str(uf.length(ss3val,0)),timerTime)
            uf.updateCell(ss3, "W"+str(uf.length(ss3val,0)),message)
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
                uf.updateCell(ss3, uf.isSplit(splits,split)+str(uf.length(ss3val,0)),timerTime)
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

class ssTable():
    def init(self,x,y,ssval):
        try:
            int(x)
            int(y)
        except:
            raise Exception("x and y must be integers")

        self.col1 = uf.getFullColumn(ssval,x)
        self.col2 = uf.getFullColumn(ssval,x+1)
        self.y = y
        self.x = x

        for i in range(y-1):
            self.col1.remove(self.col1[0])
            self.col2.remove(self.col2[0])
        
        for col in [self.col1,self.col2]:
            while "" in col:
                col.remove("")
            #col.remove(col[0])

        for i,col in enumerate(self.col1):
            self.col1[i] = int(col)
            
    def add(self,string):
        try:
            self.col1[self.col2.index(string)] += 1
        except:
            self.col2.append(string)
            self.col1.append(1)

    def update(self,ss):

        col1 = self.col1
        col2 = self.col2
        
        #for num in sorted(self.col1,reverse=True):
        #    col1.append(num)
        #    col2.append(self.col2[self.col1.index(num)])

        def comp(arg1,arg2):
            newArg1 = col1[col2.index(arg1)]
            newArg2 = col1[col2.index(arg2)]
            if newArg1 > newArg2:
                return 1
            if newArg1 < newArg2:
                return -1
            if sorted([arg1,arg2])[0] == arg1:
                return 1
            if sorted([arg1,arg2])[0] == arg2:
                return -1
            return 0

        col2 = sorted(col2, cmp=comp,reverse=True)
        col1 = sorted(col1,reverse=True)
        
        cells = []
        
        for i,cell in enumerate(col1):
            ssCell = ss.cell(self.y+1+i,self.x)
            ssCell.value = cell
            cells.append(ssCell)

        for i,cell in enumerate(col2):
            ssCell = ss.cell(self.y+1+i,self.x+1)
            ssCell.value = cell
            cells.append(ssCell)
            
        while True:
            try:
                ss.update_cells(cells)
                break
            except:
                pass
        
        self.col1 = col1
        self.col2 = col2
