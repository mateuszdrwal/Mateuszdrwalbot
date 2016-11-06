import time
from utilityFunctions import utilityFunctions

uf = utilityFunctions()

class info: #the class for setable custom commands

    def set(self,ops,username,message):#returns chat message, imput array of users that can change the text, their username and a string containing the potential new text
        if uf.isOp(ops,username):
            self.info = message.capitalize()
            return "info successfully set to " + self.info

    def get(self): 
        return self.info

class Timer:

    def __init__(self):
        self.active = False
        self.started = 0
    
    def start(self,message):
        self.started = time.time()
        
    
    def stop(self,message):
        pass

    def status(self):
        if self.active:
            return "the timer is now at " + uf.readableTime(time.time() - self.started)
        else:
            return "timer is not active"
        
    def add(self):
        pass
    
    def remove(self):
        pass
    
    def split(self,split):
        pass
